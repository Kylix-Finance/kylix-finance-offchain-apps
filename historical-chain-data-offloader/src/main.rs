use jsonrpsee::core::client::ClientT;
use jsonrpsee::rpc_params;
use jsonrpsee::ws_client::WsClientBuilder;
use serde_json::Value;
use sqlx::postgres::PgPoolOptions;
use subxt::{OnlineClient, PolkadotConfig};
use std::env;

// Kylix chain metadata
#[subxt::subxt(runtime_metadata_path = "kylix_metadata.scale")]
pub mod polkadot {}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Load environment variables
    let node_url = env::var("NODE_URL").expect("NODE_URL environment variable not set"); // wss://node_address:443
    let database_url = env::var("DATABASE_URL").expect("DATABASE_URL environment variable not set"); // postgres://username:password@tsdb_address/postgres

    // Connect to the Polkadot API
    let node_api = OnlineClient::<PolkadotConfig>::from_url(&node_url).await?;
    let mut blocks_sub = node_api.blocks().subscribe_finalized().await?;

    // Connect to the TSDB
    let pg_pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&database_url)
        .await?;

    while let Some(block) = blocks_sub.next().await {
        // Getting block number.
        let new_block = block?;
        let block_number = new_block.header().number;

        // All inserts contain the timestamp so we extract it
        let block_timestamp: u64 = node_api
            .storage()
            .at_latest()
            .await?
            .fetch(&polkadot::storage().timestamp().now())
            .await?
            .ok_or("Failed to fetch timestamp")?;
        println!("Block timestamp is {block_timestamp}! ✨");
        println!("Block number is {block_number}! ✨");

        // Create the WebSocket client
        let client = WsClientBuilder::default().build(&node_url).await?;
        // Perform the RPC call lending_getLendingPools
        let response: Value = client
            .request("lending_getLendingPools", rpc_params![])
            .await?;

        // Extract information for pools_data and dashboard_total_supply_borrow
        if let Some(lending_pools) = response[0].as_array() {
            for pool in lending_pools {
                let asset_id = pool["asset_id"].as_u64().unwrap_or(0);
                let total_pool_borrow = pool["total_pool_borrow"].as_u64().unwrap_or(0);
                let total_pool_supply = pool["total_pool_supply"].as_u64().unwrap_or(0);

                // Perform the INSERT query for pools_data
                let rows_affected = sqlx::query!(
                    "INSERT INTO pools_data (asset_id, time, total_borrow, total_supply) VALUES ($1, $2, $3, $4)",
                    asset_id as i64,
                    block_timestamp as i64,
                    total_pool_borrow as i64,
                    total_pool_supply as i64,
                )
                .execute(&pg_pool)
                .await?;

                println!("Inserted {:?} row(s)", rows_affected);
            }
        }
        // Extract information for dashboard
        let total_borrow = response[1]["total_borrow"].as_u64().unwrap_or(0);
        let total_supply = response[1]["total_supply"].as_u64().unwrap_or(0);

        // Perform the INSERT query for dashboard_total_supply_borrow
        let rows_affected = sqlx::query!(
            "INSERT INTO dashboard_total_supply_borrow (time, total_supply, total_borrow) VALUES ($1, $2, $3)",
            block_timestamp as i64,
            total_supply as i64,
            total_borrow as i64,
        )
        .execute(&pg_pool)
        .await?;

        println!("Inserted {:?} row(s)", rows_affected);
    }

    Ok(())
}
