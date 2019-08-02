// clickDistributor.js

var table = document.getElementById("distributorsTable");
if (table != null) {
    for (var i = 1; i < table.rows.length; i++) {
        for (var j = 0; j < table.rows[i].cells.length; j++)
         	table.rows[i].cells[j].onclick = inputClickHandler
    }
}

function tableText(tableCell) {
    alert(tableCell.innerHTML);
}

function inputClickHandler(e){
    e = e||window.event;
    var tdElm = e.target||e.srcElement;
    if(tdElm.style.backgroundColor == 'rgb(255, 0, 0)'){
        tdElm.style.backgroundColor = '#fff';
    } else {
        tdElm.style.backgroundColor = '#f00';
    }
}