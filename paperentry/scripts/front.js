// ephemera.

// Variables
let serverAddress;
let clientConnected = attemptConnection();

// Buttons
async function pushButton() {
    // check if connected
    clientConnected = attemptConnection();
    if(!clientConnected) {
        return;
    }

    // Get all keyword textareas
    const keywordInputs = document.querySelectorAll("textarea[name='keywords']");

    let keywords = [];

    // Append all keywords from the textareas
    keywordInputs.forEach((textarea) => {
        keywords.push(textarea.value.trim());
    });

    // Compile all data into a json
    message = {
        type: "push",
        paper: {
            $: {
                title: document.getElementById("title").value,
                authors: document.getElementById("authors").value,
                resCode: document.getElementById("resCode").value,
                batch: document.getElementById("batch").value,
                address: document.getElementById("address").value
            },
            keyword: keywords
        }
    };

    // Send data to server (w code trust me)
    id = await sendDataAndReturnID(message);

    const output = document.querySelector("#buttonOutput");
    output.textContent = "Pushed Successfully! ID is: " + id + "\n data is: " + JSON.stringify(message);;
}

// Buttons
async function deleteButton() {
    // check if connected
    clientConnected = attemptConnection();
    if(!clientConnected) {
        console.error("Disconnected from server!");
        return;
    }

    console.log(document.getElementById("idSelected").value);

    // Compile all data into a json
    message = {
        type: "delete",
        deleteID: parseInt(document.getElementById("idSelected").value)
    };

    // Send data to server (w code trust me)
    id = await sendDataAndReturnID(message);

    const output = document.querySelector("#buttonOutput");
    output.textContent = "Deleted Successfully! ID is: " + id + "\n data is: " + JSON.stringify(message);
}

function addButton() {
    // Get button and figure parent
    const button = document.getElementById('addKeyword');
    const keywordsFig = button.closest('figure');

    // Make new textarea
    const textarea = document.createElement('textarea');

    // Add attribs
    textarea.name = 'keywords';
    textarea.id = 'keywords';
    textarea.style.marginTop = '8px';

    // Add the new textarea
    keywordsFig.appendChild(textarea);
}

async function attemptConnection() {
    serverAddress = document.getElementById("ip").value;

    try {
        const response = await fetch(serverAddress + "/api/message");
        await response.json();

        console.log("connected to server.");
        document.querySelector("#ifconnected").innerText = "Status: Connected.";

        return true;
    } catch(err) {
        console.error(err);
        document.querySelector("#ifconnected").innerText = "Status: Error; Disconnected.";

        return false;
    }
}
 
// Fine I'll rename the function
async function sendDataAndReturnID(msg) {
    try {
        const response = await fetch(serverAddress + "/api/data", {
            method: "POST", // Send data using POST
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(msg)
        });

        const responseData = await response.json(); // Parse the JSON response

        console.log("Server response:", responseData);

        return responseData.id;
    } catch (err) {
        console.error("Error sending data:", err);
    }
}