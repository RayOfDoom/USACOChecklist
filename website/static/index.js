window.addEventListener("pageshow", function (event) {
    var historyTraversal = event.persisted ||
        (typeof window.performance != "undefined" &&
            window.performance.navigation.type === 2);
    if (historyTraversal) {
        // Handle page restore.
        window.location.reload();
    }
});

var curD = 0;

function display(type) {
    $("#b" + curD).removeClass("active");
    $("#b" + type).addClass("active");
    curD = type;
    var p = $(".problemlist");
    p.empty();
    for (var i = 0; i < problemlist.length; i++) {
        var problem = problemlist[i];
        if (div2int(problem["div"]) !== curD) continue;
        p.append('<tr><th class="bg-light" style="user-select:none;">' + problem["year"] + ' ' + problem["month"] + '</th><td id="' +
            problem["pid"] + '" class="Unattempted" onclick="updateStatus(this)"><div class="problem-container"><a href="http://www.usaco.org/index.php?page=viewproblem2&cpid=' +
            problem["pid"] + '" style="user-select:none;" onclick="event.stopPropagation()" target="_blank">' + problem["name"] + '  </a>' +
            '<div id="cases-' + problem["pid"] + '" class="case-info"></div></div></td></tr>');
    }

    for (var i = 0; i < checklist.length; i++) {
        var entry = checklist[i];
        var cell = $("#" + entry.pid);
        cell.removeClass("Unattempted");
        cell.addClass(entry.progress);
    }

    for (var i = 0; i < problemcases.length; i++) {
        var pcase = problemcases[i];
        var div = $("#cases-" + pcase.pid);
        console.log()
        if (pcase.correct) div.append('<div class="case case-correct" onclick="event.stopPropagation()"><div><a style="user-select:none;" target="_blank">' + pcase.symbol + '</a></div></div>')
        else div.append('<div class="case case-incorrect" onclick="event.stopPropagation()"><div><a style="user-select:none;" target="_blank">' + pcase.symbol + '</a></div></div>')
    }
}

function updateStatus(problemCell) {
    if (!allowEditing) return;
    var cur = problemCell.classList.toString()
    problemCell.classList.remove(cur);
    if (cur === "Unattempted") problemCell.classList.add("Attempted");
    else if (cur === "Attempted") problemCell.classList.add("Solved");
    else if (cur === "Solved") problemCell.classList.add("Completed");
    else problemCell.classList.add("Unattempted")

    var data = {};
    data.pid = problemCell.id;
    data.status = problemCell.classList[0];
    const request = new XMLHttpRequest();
    request.open('POST', `/update-problem/${JSON.stringify(data)}`);
    request.send();
}

function div2int(div) {
    if (div === "Bronze") return 3;
    if (div === "Silver") return 2;
    if (div === "Gold") return 1;
    return 0;
}

function copylink() {
    var text = document.getElementById("static-link");
    text.select();
    document.execCommand("copy");
}
