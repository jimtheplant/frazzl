const {ApolloServer} = require("apollo-server");
const {ApolloGateway} = require("@apollo/gateway");
const yargs = require("yargs");

const argv = yargs
    .command("start", "Start the apollo federation gateway", {
        config: {
            description: "The filename that contains a service configuration",
            alias: "c",
            type: "string"
        }
    })
    .help()
    .alias("help", "h")
    .argv
;
if(argv._.includes("start")){
    console.log("Start the server");
//     const gateway = new ApolloGateway({
//     serviceList: [
//         {name: 'test1', url: 'http://localhost:8000'},
//         {name: 'test2', url: 'http://localhost:8001'},
//     ]
// });
//
// const server = new ApolloServer({gateway, subscriptions: false});
// server.listen();
}
