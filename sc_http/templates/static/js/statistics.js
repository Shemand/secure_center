let statistics_table = undefined
function render_statistics_table(data) {
    statistics_table = new Tabulator("#statistics_table", {
        data:data,            //load row data from array
        layout:"fitColumns",      //fit columns to width of table
        tooltips:true,            //show tool tips on cells
        addRowPos:"top",          //when adding a new row, add it to the top of the table
        pagination:"local",       //paginate the data
        paginationSize:100,       //allow 7 rows per page of data
        index : 'name',
        initialSort:[             //set the initial sort order of the data
            {column:"all", dir:"asc"},
        ],
        // '#AED581' хороший цвет
        columns:[                 //define the table columns
            {title:"№", field:"rownum", align:"center", formatter : "rownum", width:50, sorter:false, editor:false},
            {title:"Подразделение", field:"structure_name", align:"center", sorter:"string"},
            {title:"Компьютеров в домене", field:"all", align:"center", sorter:"number"},
            {title:"Учетных записей заблокированно", field:"quantity_of_disabled_computers", align:"center", sorter:"number"},
            {title:"Кол-во АРМов", field:"quantity_ARMs", align:"center", sorter:"number"},
            {title:"Кол-во серверов", field:"quantity_servers", align:"center", sorter:"number"},
            {title:"С установеленным агентом и защитой", field:"kaspersky_right", align:"center", sorter:"number"},
            {title:"Без агента и защиты", field:"kaspersky_wrong", align:"center", sorter:"number"},
            {title:"% установки", field:"kaspersky_percent_right", align:"center", sorter:"number"},
            {title:"Компьютеров на Windows", field:"computers_on_windows", align:"center", sorter:"number"},
            {title:"АРМов на Windows", field:"ARMs_on_windows", align:"center", sorter:"number"},
            {title:"Серверов на Windows", field:"servers_on_windows", align:"center", sorter:"number"},
            {title:"АРМов с Dallas", field:"ARMs_with_dallas", align:"center", sorter:"number"},
            {title:"АРМов без Dallas", field:"ARMs_without_dallas", align:"center", sorter:"number"},
            {title:"% установки Dallas Lock", field:"dallas_percent_right", align:"center", sorter:"number"},
            {title:"Компьютеров на Linux", field:"computers_on_linux", align:"center", sorter:"number"},
            {title:"АРМов на Linux", field:"ARMs_on_linux", align:"center", sorter:"number"},
            {title:"Серверов на Linux", field:"servers_on_linux", align:"center", sorter:"number"},
            {title:"Компьютеров на puppet", field:"computers_on_puppet", align:"center", sorter:"number"},
            {title:"% на puppet", field:"puppet_percent_right", align:"center", sorter:"number"}
        ]
    });
}
axios({
    method : 'GET',
    url : '/api/statistics',
    withCredentials : true
}).then(function(res) {
    render_statistics_table(res.data)
})
download_button = document.getElementById('download')
download_button.addEventListener('click', function() {
    statistics_table.download("xlsx", "statistics.xlsx", {sheetName:"MyData"});
});

snapshot_dates = document.getElementById('snapshot_dates');
axios({
    url : '/api/snapshot/dates',
    method : 'GET',
    withCredentials : true
}).then(function(res) {
    data = res.data
    console.log(data);
    snapshot_dates.innerHTML = ""
    data.forEach(function(record) {
        snapshot_dates.innerHTML += '<option value="' + record.number_of_update + '">' + record.number_of_update + ' : ' + record.created + '</option>'
    });
});
snapshot_dates.addEventListener('change', function(){
    axios({
        url : '/api/statistics/id/' + snapshot_dates.value,
        method : 'GET',
        withCredentials : true
    }).then(function(res) {
        render_statistics_table(res.data)
    });
});

boxes = document.getElementsByClassName('model_columns_statistics')
Array.from(boxes).forEach(function(element) {
    element.checked = true
    element.addEventListener('change', function(event) {
        if (event.target.checked)
            statistics_table.showColumn(element.attributes.name.value)
        else
            statistics_table.hideColumn(element.attributes.name.value)
    });
});

disable_all_column = document.getElementById('disable_all_columns')
disable_all_column.addEventListener('click', function() {
    Array.from(boxes).forEach(function(element) {
        element.checked = false
        statistics_table.hideColumn(element.attributes.name.value)
    });
});