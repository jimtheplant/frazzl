const {ApolloServer, RemoteGraphQLDataSource} = require("apollo-server");
const {ApolloGateway} = require("@apollo/gateway");
const fs = require("fs");
const yargs = require("yargs");

function parse_service_config(service) {
    const service_config = {};
    service_config.name = service.service_name;
    if(service.type === "external"){
        service_config.url = service.url;
    }
    else if(service.type === "local"){
        let port = service.port;
        service_config.url = `http://localhost:${port}`
    }
    return service_config;
}


async function start_gateway(federation) {
    let serviceList = federation.map(item => parse_service_config(item));
    const gateway = new ApolloGateway({
        serviceList: serviceList
    });
    try{
        gatewayConfig = await gateway.load();
        const server = new ApolloServer({...gatewayConfig, subscriptions: false});
        server.listen();
    }
    catch (e) {
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
                if(e.code !== "MODULE_NOT_FOUND") throw e;
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

