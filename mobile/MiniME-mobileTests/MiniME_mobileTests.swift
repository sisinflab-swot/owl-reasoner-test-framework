//
//  Created by Ivano Bilenchi on 10/07/17.
//  Copyright © 2017 SisInf Lab. All rights reserved.
//

import XCTest
import OWLAPI
import MiniME

class MiniME_mobileTests: XCTestCase {
    
    // MARK: XCTestCase
    
    override func setUp() {
        super.setUp()
        // Put setup code here. This method is called before the invocation of each test method in the class.
    }
    
    override func tearDown() {
        // Put teardown code here. This method is called after the invocation of each test method in the class.
        super.tearDown()
    }
    
    func testClassification() {
        standardTest(withName: "classification") { (ontology) in
            let start = mach_absolute_time()
            
            let reasoner = MicroReasoner(ontology: ontology)
            reasoner.kb.classify()
            
            let end = mach_absolute_time()
            return (start, end)
        }
    }
    
    func testConsistency() {
        standardTest(withName: "consistency") { (ontology) in
            let start = mach_absolute_time()
            
            let reasoner = MicroReasoner(ontology: ontology)
            _ = reasoner.isConsistent()
            
            let end = mach_absolute_time()
            return (start, end)
        }
    }
    
    func testAbductionContraction() {
        
        let resourceUrl = ontologyUrl(forEnvVar: "RESOURCE")!
        let requestUrl = ontologyUrl(forEnvVar: "REQUEST")!
        
        let resourceName = resourceUrl.deletingPathExtension().lastPathComponent
        let requestName = requestUrl.deletingPathExtension().lastPathComponent
        
        Logger.stdOut.log("Computing semantic match between resource \"\(resourceName)\" and request \"\(requestName)\"")
        
        autoreleasepool {
            
            let resource = loadOntology(atUrl: resourceUrl, printTitle: "Resource parsing")
            let request = loadOntology(atUrl: requestUrl, printTitle: "Request parsing")
            
            var start = mach_absolute_time()
            let reasoner = MicroReasoner(ontology: resource)
            var end = mach_absolute_time()
            
            Logger.stdOut.logMillis(between: start, and: end, title: "Reasoner initialization")
            
            start = mach_absolute_time()
            
            let resourceIndividuals = reasoner.resourceIndividuals.values
            let requestIndividuals = reasoner.loadRequest(from: request).values
            
            for resourceIndividual in resourceIndividuals {
                for requestIndividual in requestIndividuals {
                    
                    let resourceIri = resourceIndividual.iri
                    var requestIri = requestIndividual.iri
                    
                    if let compatible = reasoner.compatibility(betweenResource: resourceIri, andRequest: requestIri) {
                        
                        if !compatible, let contraction = reasoner.contraction(withResource: resourceIri, forRequest: requestIri) {
                            requestIri = OWLIRI(string: requestIri.string + "_compatible_" + resourceIri.string)
                            reasoner.loadRequest(individual: Item(name: requestIri, description: contraction.keep))
                        }
                        
                        _ = reasoner.abduction(withResource: resourceIri, forRequest: requestIri)
                    }
                }
            }
            
            end = mach_absolute_time()
            
            Logger.stdOut.logMillis(between: start, and: end, title: "Reasoning")
            logMaxMemory()
        }
    }
    
    // MARK: Private methods
    
    private func loadOntology(atUrl url: URL, printTitle: String) -> OWLOntology {
        let start = mach_absolute_time()
        let ontology = try! OWLManager.createOWLOntologyManager().loadOntologyFromDocument(at: url)
        let end = mach_absolute_time()
        
        Logger.stdOut.logMillis(between: start, and: end, title: printTitle)
        return ontology
    }
    
    private func logMaxMemory() {
        var usage = rusage()
        getrusage(RUSAGE_SELF, &usage)
        
        Logger.stdOut.log("Memory: \(usage.ru_maxrss) B")
    }
    
    private func ontologyUrl(forEnvVar envVar: String) -> URL! {
        
        guard let resourceName = ProcessInfo.processInfo.environment[envVar] else {
            XCTFail("Environment variable \"\(envVar)\" not set.")
            return nil
        }
        
        guard let resource = Bundle(for: type(of: self)).url(forResource: resourceName, withExtension: "owl") else {
            XCTFail("No ontology named \"\(resourceName)\".")
            return nil
        }
        
        return resource
    }
    
    private func standardTest(withName name: String, handler: (OWLOntology) -> (start: UInt64, end: UInt64)) {
        
        let resource = ontologyUrl(forEnvVar: "RESOURCE")!
        Logger.stdOut.log("Computing \(name) for \"\(resource.deletingPathExtension().lastPathComponent)\"")
        
        autoreleasepool {
            let ontology = loadOntology(atUrl: resource, printTitle: "Parsing")
            
            let stats = handler(ontology)
            Logger.stdOut.logMillis(between: stats.start, and: stats.end, title: "Reasoning")
            
            logMaxMemory()
        }
    }
}
