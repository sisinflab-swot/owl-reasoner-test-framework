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
    
    // MARK: Private methods
    
    private func standardTest(withName name: String, handler: (OWLOntology) -> (start: UInt64, end: UInt64)) {
        
        guard let resourceName = ProcessInfo.processInfo.environment["RESOURCE"] else {
            XCTFail("No resource specified for the classification task.")
            return
        }
        
        Logger.stdOut.log("Computing \(name) for \"\(resourceName)\"")
        
        guard let resource = Bundle(for: type(of: self)).url(forResource: resourceName, withExtension: "owl") else {
            XCTFail("No resource named \"\(resourceName)\".")
            return
        }
        
        autoreleasepool {
            let manager = OWLManager.createOWLOntologyManager()
            
            let start = mach_absolute_time()
            let ontology = try! manager.loadOntologyFromDocument(at: resource)
            let end = mach_absolute_time()
            
            Logger.stdOut.logMillis(between: start, and: end, title: "Parsing")
            
            let stats = handler(ontology)
            Logger.stdOut.logMillis(between: stats.start, and: stats.end, title: "Reasoning")
            
            var usage = rusage()
            getrusage(RUSAGE_SELF, &usage)
            
            Logger.stdOut.log("Memory: \(usage.ru_maxrss) B")
        }
    }
}
