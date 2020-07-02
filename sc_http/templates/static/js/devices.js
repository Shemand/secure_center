let table;

name_input = document.getElementById('add_device_name')
cg_input = document.getElementById('add_device_cg')
ip_input = document.getElementById('add_device_ip')
type_input = document.getElementById('add_device_type')
comment_input = document.getElementById('add_device_comment')

ok_button = document.getElementById('add_device_OKButton')
cancel_button = document.getElementById('add_device_CancelButton')

function onChangeCryptoGateway() {
    axios({
        method : 'GET',
        url : '/api/available/ip/crypto_gateway/' + cg_input.value,
        withCredentials : true
    }).then(function(res) {
        ip = res.data
        console.log(ip)
        ip_input.innerHTML = ""
        ip.forEach(function(element){
            ip_input.innerHTML = ip_input.innerHTML + '<option>' + element + '</option>'
        });
    })
}

axios({
    method : 'GET',
    url : '/api/available/crypto_gateways',
    withCredentials : true
}).then(function(res) {
    gateways = res.data
    cg_input.innerHTML = ""
    gateways.forEach(function(element){
        cg_input.innerHTML = cg_input.innerHTML + '<option>' + element + '</option>'
    });
    onChangeCryptoGateway()
})

ok_button.addEventListener('click', function() {
    if (name_input && cg_input && ip_input && type_input) {
        axios({
            method : 'PUT',
            url : '/api/devices',
            withCredentials : true,
            data : {
                name : name_input.value,
                crypto_gateway : cg_input.value,
                ip : ip_input.value,
                type : type_input.value,
                comment : comment_input.value
            }
        }).then(function(res) {
            if (res.data) {
                table.addRow({
                    unit : res.data.data.unit,
                    CG_name : res.data.data.CG_name,
                    name : res.data.data.name,
                    ip : res.data.data.ip,
                    type : res.data.data.type,
                    comment : res.data.data.comment
                })
            }
        })
    } else {
        console.log('not all field was filled')
    }
})

function delete_computer(computername, id) {
    axios({
        method : 'DELETE',
        url : '/api/devices/' + computername,
        withCredentials : true
    }).then(function(res) {
        if (res.data.status == "ok") {
            table.deleteRow(computername)
        }
    })
}

axios({
    method : 'GET',
    url : '/api/devices',
    withCredentials : true
}).then(function(res) {
    table = new Tabulator("#table", {
    data:res.data,           //load row data from array
    layout:"fitColumns",      //fit columns to width of table
    tooltips:true,            //show tool tips on cells
    addRowPos:"top",          //when adding a new row, add it to the top of the table
    pagination:"local",       //paginate the data
    paginationSize:100,         //allow 7 rows per page of data
    index : 'name',
    initialSort:[             //set the initial sort order of the data
        {column:"name", dir:"asc"},
    ],
    // '#AED581' хороший цвет
    columns:[                 //define the table columns
        {title:"№", align:"center", formatter : "rownum", width:50, sorter:false, editor:false},
        {title:"Подразделение", field:"unit", align:"center", sorter:"string", width:75, headerFilter:"select", headerFilterParams:{values:true, verticalNavigation : "editor"}},
        {title:"КШ", field:"CG_name", align:"center", sorter:"string", width:75, headerFilter:"select", headerFilterParams:{values:true, verticalNavigation : "editor"}},
        {title:"Имя компьютера", field:"name", align:"center", sorter:"string", headerFilter:true},
        {title:"IP", field:"ip", align:"center", headerFilter:true, editor:false, formatter:function(cell){
            if( cell.getValue() == "Неизвестно" ) {
                cell.getElement().style.backgroundColor = '#FCE4EC';
            }
            return cell.getValue()
        }},
        {title:"Тип устройства", field:"type", align : "center", editor:"select", editorParams:{values:{"1" : "Управляемый коммутатор",
                                                                                                        "2" : "Сетевой принтер",
                                                                                                        "3" : "IP камера",
                                                                                                        "4" : "ИБП"}},
                                                                formatter : function(cell) {
                                                                    if (cell.getValue() == 1) return "Управляемый коммутатор"
                                                                    if (cell.getValue() == 2) return "Сетевой принтер"
                                                                    if (cell.getValue() == 3) return "IP камера"
                                                                    if (cell.getValue() == 4) return "ИБП"
                                                                },
                                                                cellEdited: function(cell){
                                                                    dataToSend = {};
                                                                    row = cell.getRow();
                                                                    devicename = row.getCell('name').getValue();
                                                                    axios({
                                                                        method : "POST",
                                                                        url : "/api/table/device/" + devicename + "/type/" + cell.getValue(),
                                                                        data : dataToSend,
                                                                        withCredentials : true
                                                                    })
                                                                    .then(function() {
                                                                        console.log('all right')
                                                                    })
                                                                    .catch(function() {
                                                                        console.log('something wrong')
                                                                    });
                                                                }},
        {title:"Комментарий", field: "comment", editor:"textarea", width: 200, headerFilter:true, cellEdited:function(cell) {
            dataToSend = {}
            row = cell.getRow();
            devicename = row.getCell('name').getValue();
            dataToSend.comment = cell.getValue();
            axios({
                method : 'POST',
                url : '/api/table/device/' + devicename + '/comment/',
                data : dataToSend,
                withCredentials : true
            }).then(function() {
                console.log('all right');
            }).catch(function() {
                console.log("we have some troubles");
            });
        }},
        {formatter: function formatters_buttons_cell(cell, formatterParams) {
            space = '<span> </span>'
            id = cell.getRow().getIndex()
            devicename = cell.getData().name
            let onclick = 'delete_computer(\'' + devicename + '\', \'' + id + '\')';
            console.log(onclick)
            delete_button = '<input type="button" value="X" id="delete_button_' + devicename + '" class="block_item" onclick="' + onclick + '" >'
            return delete_button
        }, width:70}
    ]})
})