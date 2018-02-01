# OWL Reasoner Test Framework

Test framework used to evaluate correctness/completeness and performance of inference tasks implemented by OWL reasoners.
The current release is mainly meant as a test suite for the [Mini-ME](http://sisinflab.poliba.it/swottools/minime) mobile reasoner and matchmaking engine.

## Using the framework

The framework can be used on any computer running **macOS** 10.11 El Capitan and later.

### Installing the framework

- Install the *python3* interpreter. If you use *HomeBrew*: `brew install python3`
- Clone this project: `git clone --recursive git@github.com:sisinflab-swot/owl-reasoner-test-framework.git`

### Configuring the tests

Datasets must be placed into the `data` directory. Each dataset should have the following directory structure:

```
+-- dataset_name
    +-- functional
    |   +-- ontology1.owl
    |   +-- ontology2.owl
    +-- rdfxml
        +-- ontology1.owl
        +-- ontology2.owl
```

Reasoners can be integrated by implementing the `reasoners.owl.OWLReasoner` interface and adding reasoner instances to the `config.Reasoners.ALL` variable.

### Running the tests

Tests can be run by launching the `test` executable from the command line:

`./test <test name> -m <test mode>`

As an example, to run the classification time test: `./test classification -m time`

For more information about the implemented tests, test modes and additional available flags, you can invoke `./test -h` or `./test <test name> -h`

**Note:** for mobile tests, you first need to run the test target via Xcode once, in order to install the test application on the connected device.

## License

*OWL Reasoner Test Framework* is distributed under the [Eclipse Public License, Version 1.0](https://www.eclipse.org/legal/epl-v10.html).
