var curD = 0;

function display(type) {
    $("#b" + curD).removeClass("active");
    $("#b" + type).addClass("active");
    curD = type;
    var p = $(".problemlist");
    p.empty();
    var prevyear = problemlist[0]["year"], prevmonth = problemlist[0]["month"];
    p.append('<tr>')
    p.append('<th class="bg-light" style="user-select:none;">' + problemlist[0]["year"] + ' ' + problemlist[0]["month"] + '</th>');
    for (var i = 0; i < problemlist.length; i++) {
        var problem = problemlist[i];
        if (curD === 0 && problem["div"] !== "Platinum") continue;
        if (curD === 1 && problem["div"] !== "Gold") continue;
        if (curD === 2 && problem["div"] !== "Silver") continue;
        if (curD === 3 && problem["div"] !== "Bronze") continue;
        if (problem["year"] !== prevyear || problem["month"] !== prevmonth) {
            p.append('</tr>')
            p.append('<tr>');
            p.append('<th class="bg-light" style="user-select:none;">' + problem["year"] + ' ' + problem["month"] + '</th>');
        }
        p.append('<td id="' + problem["pid"] + '" class="Unattempted" onclick="updateStatus(this)"><a href="http://www.usaco.org/index.php?page=viewproblem2&cpid=' + problem["pid"] + '" style="user-select:none;" onclick="event.stopPropagation()" target="_blank">' + problem["name"] + '</a></td>');
        prevyear = problem["year"];
        prevmonth = problem["month"];
    }
    p.append('</tr>');

    for (var i = 0; i < checklist.length; i++) {
        var entry = checklist[i];
        var cell = $("#" + entry.pid);
        cell.removeClass("Unattempted");
        cell.addClass(entry.progress);
    }
}


function updateStatus(problemCell) {
    var cur = problemCell.classList.toString()
    problemCell.classList.remove(cur);
    if (cur === "Unattempted") problemCell.classList.add("Attempted");
    else if (cur === "Attempted") problemCell.classList.add("Solved");
    else if (cur === "Solved") problemCell.classList.add("Completed");
    else problemCell.classList.add("Unattempted")

    const request = new XMLHttpRequest();
    var data = {};
    data.pid = problemCell.id;
    data.status = problemCell.classList[0];
    request.open('POST', `/update_problems/${JSON.stringify(data)}`);
    request.send();
}