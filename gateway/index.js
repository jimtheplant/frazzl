const { ApolloServer } = require("apollo-server");
const { ApolloGateway } = require("@apollo/gateway");

const gateway = new ApolloGateway({
  serviceList: [
    { name: 'test1', url: 'http://localhost:8000' },
    { name: 'test2', url: 'http://localhost:8001' },
  ]
});

const server = new ApolloServer({ gateway, subscriptions: false });
server.listen();