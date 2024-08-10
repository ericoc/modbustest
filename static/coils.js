async function sendAll (coils, action) {
    for (const coil of coils) {
        if (action === "read") {
            await coil.read();
        }
        if (action === "toggle") {
            await coil.toggle();
        }
    }
}

async function updateCounts (coils) {
    let totalCount = 0;
    let activeCount = 0;
    let inactiveCount = 0;
    for (const coil of coils) {
        totalCount++;
        if (coil.value === true) { activeCount++; }
        if (coil.value === false) { inactiveCount++; }
    }
    document.getElementById("totalCount").innerText = totalCount.toString();
    document.getElementById("activeCount").innerText = activeCount.toString();
    document.getElementById("inactiveCount").innerText = inactiveCount.toString();
    document.getElementById("coilCounts").style.display = "block";
}

const coils = [];

const Coil = class {

    constructor(number, value) {

        this.number = number;
        this.value = value;

        const coilListItem = document.createElement("div");
        coilListItem.className = "list-group-item";

        const checkSwitchDiv = document.createElement("div");
        checkSwitchDiv.className = "form-check form-switch list-group-item-text";

        const checkSwitchLabel = document.createElement("label");
        checkSwitchLabel.className = "form-check-label fw-bold";
        checkSwitchLabel.for = this.number;
        checkSwitchLabel.innerText = this.number;

        const checkSwitchInput = document.createElement("input");
        checkSwitchInput.className = "form-check-input";
        checkSwitchInput.type = "checkbox";
        checkSwitchInput.role = "switch";
        checkSwitchInput.name = this.number
        checkSwitchInput.id = this.number;
        checkSwitchInput.onclick = () => { this.toggle(); };
        this.button = checkSwitchInput;
        this.read();

        checkSwitchDiv.appendChild(checkSwitchLabel);
        checkSwitchDiv.appendChild(checkSwitchInput);
        coilListItem.appendChild(checkSwitchDiv);
        document.getElementById("coilList").appendChild(coilListItem);
    };

    async send(method) {
        const xhr = new XMLHttpRequest()
        await xhr.open(method, `/api/${this.number}/`)
        await xhr.send()
        xhr.onreadystatechange = async () => {
            if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
                this.button.checked = JSON.parse(xhr.responseText)["coils"][this.number];
                this.value = this.button.checked;
                await updateCounts(coils);
            }
        };
    };

    async read() { return this.send("GET"); };
    async toggle() { return this.send("POST"); };
};
