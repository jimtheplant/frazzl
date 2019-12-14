const {ApolloServer} = require("apollo-server");
const {ApolloGateway} = require("@apollo/gateway");
const fs = require("fs");
const yargs = require("yargs");

async function start_gateway(federation) {
    const gateway = new ApolloGateway({
        serviceList: federation
    });
    try {
        const gatewayConfig = await gateway.load();
        const server = new ApolloServer({...gatewayConfig, subscriptions: false});
        server.listen();
    } catch (e) {
        console.log("Apollo Gateway could not be started. Exiting...");
        console.log(e);
        process.exit(1);
    }
}


argv = yargs
    .command("start <config>", "Start the apollo federation gateway", yargs => {
            return yargs.positional("config", {
                type: "string",
                desc: "The filename that contains a service configuration"
            })
        },
        args => {
            try {
                const apollo_config = JSON.parse(fs.readFileSync(args.config));
                start_gateway(apollo_config.federation)
            } catch (e) {
                if (e.code !== "MODULE_NOT_FOUND") throw e;
                console.log(args.config);
                console.log("Config file could not be loaded... exiting");
                process.exit(1);
            }
        }
    )
    .demandCommand()
    .help()
    .alias("help", "h")
    .argv
;

