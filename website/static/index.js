var curD = 0;

function display(type) {
    $("#b" + curD).removeClass("active");
    $("#b" + type).addClass("active");
    curD = type;

    var table, tr, td, i, diff;
    table = document.getElementById("problems");
    tr = table.getElementsByTagName("tr");

    for (i = 0; i < tr.length; i++) {
        td = tr[i].getElementsByTagName("td")[0];
        if (td) {
            td.style.display = "none";
            diff = td.textContent || td.innerText;
            if (diff === "Bronze" && curD === 3) {
                tr[i].style.display = "";
            } else if (diff === "Silver" && curD === 2) {
                tr[i].style.display = "";
            } else if (diff === "Gold" && curD === 1) {
                tr[i].style.display = "";
            } else if (diff === "Platinum" && curD === 0) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}


var table = document.getElementById("problems");
if (table != null) {
    for (var i = 1; i < table.rows.length; i++) {
        for (var j = 1; j < table.rows[i].cells.length; j++) {
            table.rows[i].cells[j].onclick = function () {
                console.log(this.tagName);
                updateStatus(this);
                const request = new XMLHttpRequest();
                var data = {};
                data.pid = this.id;
                data.status = this.classList[0];
                request.open('POST', `/update_problems/${JSON.stringify(data)}`);
                request.send();
            };
        }
    }
}


function updateStatus(problemCell) {
    var cur = problemCell.classList.toString()
    problemCell.classList.remove(cur);
    if (cur === "Unattempted") problemCell.classList.add("Attempted");
    else if (cur === "Attempted") problemCell.classList.add("Solved");
    else if (cur === "Solved") problemCell.classList.add("Completed");
    else problemCell.classList.add("Unattempted")
}