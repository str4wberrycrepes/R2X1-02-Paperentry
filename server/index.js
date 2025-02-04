// ephemera.

// import
const express = require("express");
const cors = require("cors");
const fs = require("fs");
const xml2js = require("xml2js");

// variables
const xmlFilePath = "./xml/data.xml"
let id;

const app = express();
app.use(cors()); //enable cross origin
app.use(express.json()); //allow json requests

// get
app.get("/api/message", (req, res) => {
    res.json({ message: "Hi." });
});

// post
app.post("/api/data", (req, res) => {
    const receivedData = req.body; // Get the JSON data sent from frontend
    console.log("Received data:", receivedData); // Log it on the server

    // Very sily way of handling it but it is TWO in the morning
    if(receivedData.type == "delete") {
        updateXML(receivedData.deleteID, res, 0);
    } else if(receivedData.type == "push") {
        updateXML(receivedData, res, 1);
    } else {
        console.error("Client sent incorrect type,");
    }
});

// Start the server
const PORT = 5000;
app.listen(PORT, '0.0.0.0', () => console.log(`Server running on port ${PORT}`));

function updateXML(json, res, mode) {
    // Read xml file
    fs.readFile(xmlFilePath, 'utf8', (err, data) => {
        // Error handling
        if (err) {
            console.error('Error reading file (XML):', err);
            return;
        }
    
        // Parse XML into object
        xml2js.parseString(data, (err, result) => {
            // Error handling once again (y r computers so finnicky bruh)
            if (err) {
                console.error('Error parsing XML:', err);
                return;
            }

            // do NOT ask me about ANYTHING, I wrote the succeeding lines in an incorrect state of mind.

            let resultant = {paper: []};

            if(mode == 0) {
                // get id of target to delete
                let targetID = json;

                // check if it exists, then remove from array
                if(result.research_papers.paper && result.research_papers.paper[targetID]) {
                    console.log(result.research_papers.paper[targetID]);
                    delete result.research_papers.paper[targetID];
                } else {
                    // Send a response back to the frontend
                    res.json({ message: "XML is empty.", id: targetID, json }); // The code totally has to be here specifically trust me bro
                    return;
                }

                // push data into resultant
                if(result.research_papers.paper) {
                    result.research_papers.paper.forEach(element => {
                        resultant.paper.push(element);
                    });
                }

                // Send a response back to the frontend
                res.json({ message: "Data deleted successfully!", id: targetID, json }); // The code totally has to be here specifically trust me bro
            }
    
            if(mode == 1) {
                // reset id counter
                id = 0;
                
                //push data into resultant
                if(result.research_papers.paper) {
                    result.research_papers.paper.forEach(element => {
                        resultant.paper.push(element);
                        id++;
                    });
                }
                
                json.paper.$.id = id; // add simple id to paper
                resultant.paper.push(json.paper); // push paper sent from front into papers
    
                // Send a response back to the frontend
                res.json({ message: "Data received successfully!", id: id, json }); // The code totally has to be here specifically trust me bro
            }

            // Convert object back to XML
            const builder = new xml2js.Builder({ headless: true, rootName: "research_papers"});
            const xml = builder.buildObject(resultant);

            // Write updated XML back to file
            fs.writeFile(xmlFilePath, xml, 'utf8', err => {
                if (err) {
                    console.error('Error writing to file (XML):', err);
                } else {
                    console.log('XML file updated!');
                }
            });
        });
    });
}
