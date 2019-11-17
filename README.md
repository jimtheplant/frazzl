# frazzl

## About
Frazzl is a graphql framework for implementing the 
apollo federation [specification](https://www.apollographql.com/docs/apollo-server/federation/introduction/).
The framework aims to make developing microservices for graphql servers easier. 
It is currently in the very early prototyping stage and actively seeking contributions.

## Table of contents
[frazzl](#frazzl)
* [About](#about)
* [Requirements](#requirements)
* [Installation](#installation)
* [Features](#features)
    * [Apollo federation](#apollo-federation-specification)
    * [Functional Resolvers](#functional-field-resolution)
    * [Command Line Tooling](#command-line-tooling-future)
    * [Modularity](#service-modularity)
    * [Testing Helpers](#testing-library-future)
* [Usage](#usage)
    * [Core Ideas](#core-ideas)
    * [Project Structure](#project-structure)
    * ["Hello World" App](#hello-world-app)
    * [Other Examples](#other-examples)
* [Learning Resources](#learning-resources)
* [Contributing](#contributing--reporting-issues)
* [License](#license)
* [Acknowledgments](#acknowledgements)

## Requirements

## Installation

Frazzl can be installed from [pip](https://pypi.org/project/pip/)

```
> pip install frazzl
``` 

The framework must be initialized using the command line tool.

```
> frazzl init
```

## Features
Frazzl has several major features implemented or on the roadmap.

#### Apollo Federation specification
A basic implementation of the specification is available that allows developers to 
define queries that are relevant to their service, with little boilerplate logic. 

#### Functional Field Resolution
Create reusable resolvers for fields within a graphql schema. 
The framework encourages functional design by having well defined 
inputs and outputs for all field resolvers.

###### Future Plans
* Auto-running resolver tests on startup
* Support for simple 3rd party integrations ([SQLAlchemy](https://www.sqlalchemy.org/), [PyMongo](https://api.mongodb.com/python/current/))
* Security helpers

#### Command Line Tooling (Future)
Similar to [Django](https://www.djangoproject.com/), frazzl will have a command line tool kit for project creation. 
Create a simple app for a small tutorial project or use a user created template.

#### Service Modularity
Have local services dependent on each other? Define where it's located and frazzl will integrate it seamlessly into 
its gateway endpoint. Don't need a full service but want to access already created resolvers? 
Define it in your config and let the framework do the rest. 

###### Future Plans
* Defining external service directories
* Docker integration
* Packaging helper

#### Testing library (Future)
Untested code is **bad** code, therefore Booster makes it less awful to write tests. Spend more time doing feature development
and creating cool stuff.

###### Future Plans
* Fully tested framework (Whoops)
* Auto generated test stubs
* Service validator: Make sure your service is deployable with integration tests!

## Usage
### Core Ideas
The apollo federation is a specification for a unified graphql schema. The main idea
is to run a gateway node in front of many services that implement the specification. The gateway node will expose a single 
schema that is a union of the microservices' schemas. When the gateway node receives a query, it will send queries the microservices
needed to compose the response. By properly implementing the specification and defining the dependency services, 
the [apollo-gateway](https://github.com/apollographql/apollo-server/tree/master/packages/apollo-gateway)
node will be able to unify all active microservice schemas into a single queryable endpoint.

This project helps with the development of these dependency services. A user can define a *mostly* normal graphql schema,
and the framework will implement the specification on top. Frazzl can also start a local gateway node and other 
Booster services locally to assist in development and testing. 

### Project Structure
Frazzl takes inspiration from [django](https://www.djangoproject.com/) for it's recommended project structure.
 
### "Hello World" App
TODO: Example
### Other Examples

## Learning Resources
#### GraphQL
* [Basics](https://graphql.org/)
* [Ariadne](https://ariadnegraphql.org/docs/intro)
#### Apollo Federation
* [Basics](https://www.apollographql.com/docs/apollo-server/federation/introduction/)
* [TLDR](https://www.codewall.co.uk/an-introduction-tutorial-to-apollo-graphql-federation/)
* [Specification Video](https://www.youtube.com/watch?v=lRI0HfXBAm8)
### Jimtheplant's Stream
I occasionally stream my development on Twitch,
check me out [here](https://www.twitch.tv/jimtheplant)!

## Contributing / Reporting issues
I am actively looking for help on github. Feel free to log issues there or drop in
to one of my streams.
 
## License

[Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0.html)

## Acknowledgements
* [Ariadne](https://ariadnegraphql.org)
* [Apollo](https://www.apollographql.com/)

Thank you to my friends who have helped me out too!
