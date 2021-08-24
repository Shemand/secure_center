let filter_block = document.getElementById("filter_block");
let search_block = document.getElementById("search_block");
let search_input = document.getElementById("search_input")
let select_unit = document.getElementById("select_unit")
let search_type = document.getElementById("search_type")
let DL_options = document.getElementById("DL_options");
let KL_options = document.getElementById("KL_options");
let os_options = document.getElementById("OS_options");
let set_filter_button = document.getElementById("set_filter");
let clear_filter_button = document.getElementById("clear_filter");

let isGoodDL = document.getElementById("is_good_dl");
let isWithoutDL = document.getElementById("is_without_dl");
let isErrorDL = document.getElementById("is_error_dl");

let isGoodAgent = document.getElementById("is_good_agent");
let isGoodSecurity = document.getElementById("is_good_security");
let isWithoutAgent = document.getElementById("is_without_agent");
let isWithoutSecurity = document.getElementById("is_without_security");
let isErrorAgent = document.getElementById("is_error_agent");
let isErrorSecurity = document.getElementById("is_error_security");

let isWindows = document.getElementById("is_windows");
let isLinux = document.getElementById("is_linux");
let isUnknown = document.getElementById("is_unknown");

is_inDomain = document.getElementById("is_inDomain");
is_notDomain = document.getElementById("is_notDomain");

is_klIP = document.getElementById("is_klIP");
is_Active = document.getElementById('is_Active');
is_notActive = document.getElementById('is_notActive');

is_all_computer_types = document.getElementById('is_all_computer_types')
is_some_computer_types = document.getElementById('is_some_computer_types')
is_computer_type_ARM = document.getElementById('is_computer_type_ARM')
is_computer_type_server = document.getElementById('is_computer_type_server')

let table_control_panel = document.getElementById("control_panel");
let open_filters_button = document.getElementById("open_filters");
let open_macroses_button = document.getElementById("open_macroses");
let filter_status_bar = document.getElementById("filter_status_bar")
let filter_status = document.getElementById("filter_status")
let macroses_block = document.getElementById("macroses_block");

let mc_without_agent = document.getElementById("mc_without_agent");
let mc_without_security = document.getElementById("mc_without_security");
let mc_wrong_agent = document.getElementById("mc_wrong_agent");
let mc_wrong_security = document.getElementById("mc_wrong_security");
let mc_problems_kl = document.getElementById("mc_problems_kl");
let mc_without_dl = document.getElementById("mc_without_dl");
let mc_problems_dl = document.getElementById("mc_problems_dl");
let mc_without_domain = document.getElementById("mc_without_domain");
let mc_isActive = document.getElementById("mc_isActive");

let outer_last_updated = document.getElementById("outer_last_updated");
let inner_last_updated = document.getElementById("inner_last_updated");

let download_button = document.getElementById("download");

let good_agent_versions = ['11.0.0.29','11.0.0.1131','11.0.0.1131']
let good_security_versions = ['10.1.1.6421','11.1.1.126','10.1.2.996','11.0.0.1131']

user_isAdmin = undefined
axios({method:"GET", url:"api/user/isadmin", withCredentials:true}).then(function(res) {
    if (res.data['status'] == 'ok')
        user_isAdmin = true
    else
        user_isAdmin = false
})

function unlock_computer(computername) {
    axios({method:"POST", url:"api/computer/unlock/" + computername, withCredentials:true}).then(function() {
        button = document.getElementById("unlock_button_" + computername);
        button.hidden = true
    });
}

function lock_computer(computername) {
    axios({method:"POST", url:"api/computer/lock/" + computername, withCredentials:true}).then(function() {
        button = document.getElementById("lock_button_" + computername);
        button.hidden = true
    });
}

let stat = {
    all : document.getElementById('stat_all').getElementsByClassName('stat_value')[0],
    domain : document.getElementById('stat_domain').getElementsByClassName('stat_value')[0],
    dl : document.getElementById('stat_dl').getElementsByClassName('stat_value')[0],
    agent : document.getElementById('stat_agent').getElementsByClassName('stat_value')[0],
    security : document.getElementById('stat_security').getElementsByClassName('stat_value')[0],
    windows : document.getElementById('stat_windows').getElementsByClassName('stat_value')[0],
    linux : document.getElementById('stat_linux').getElementsByClassName('stat_value')[0],
    unknown : document.getElementById('stat_unknown_os').getElementsByClassName('stat_value')[0]
}

let networkInfo = {
    all : 0,
    inDomain : 0,
    dl : 0,
    agent : 0,
    security : 0,
    windows : 0,
    linux : 0,
    unknown : 0
}

let current_statistic = new Object();
Object.assign(current_statistic, networkInfo)

function updateStatistic(table) {
    current_statistic = new Object();
    Object.assign(current_statistic, networkInfo);
    let rows = table.getRows("active");
    rows.forEach(function(elem) {
        tmpData = elem.getData();
        current_statistic.all++;
        if(tmpData.ad != "Не зарегистрирован")
            current_statistic.inDomain++;
        if(tmpData.dallas != "Отсутствует")
            current_statistic.dl++;
        if(tmpData.kl_agent != "Отсутствует")
            current_statistic.agent++;
        if(tmpData.kl_security != "Отсутствует")
            current_statistic.security++;
        if(tmpData.os == "Windows")
            current_statistic.windows++;
        if(tmpData.os == "Linux")
            current_statistic.linux++;
        if(tmpData.os == "Неизвестно")
            current_statistic.unknown++;
    });
    stat.all.innerHTML = current_statistic.all;
    stat.domain.innerHTML = current_statistic.inDomain;
    stat.dl.innerHTML = current_statistic.dl;
    stat.agent.innerHTML = current_statistic.agent;
    stat.security.innerHTML = current_statistic.security;
    stat.windows.innerHTML = current_statistic.windows;
    stat.linux.innerHTML = current_statistic.linux;
    stat.unknown.innerHTML = current_statistic.unknown;
}

function updateFilterStatus() {
    let status_info = {
        dallas : [],
        kaspersky : [],
        os : [],
        domain : []
    };
    if(isGoodDL.checked)
        status_info.dallas.push("Установлен Dallas Lock");
    if(isWithoutDL.checked)
        status_info.dallas.push("Не установлен Dallas Lock");
    if(isErrorDL.checked)
        status_info.dallas.push("Dallas Lock установлен с ошибкой");

    if(isGoodAgent.checked)
        status_info.kaspersky.push("Установлен правильный Agent Касперского");
    if(isGoodSecurity.checked)
        status_info.kaspersky.push("Установлен правильная защита Касперского");
    if(isWithoutAgent.checked)
        status_info.kaspersky.push("Не установлен Агент Касперского");
    if(isWithoutSecurity.checked)
        status_info.kaspersky.push("Не установлена защита Касперского");
    if(isErrorAgent.checked)
        status_info.kaspersky.push("Установлена не правильная версия агента Касперского");
    if(isErrorSecurity.checked)
        status_info.kaspersky.push("Установленна неправильная версия защиты Касперского");
    if(is_klIP.checked)
        status_info.kaspersky.push("Машины, без IP адреса касперского");

    if(isWindows.checked)
        status_info.os.push("Машины под управлением ОС Windows");
    if(isLinux.checked)
        status_info.os.push("Машины под управлением ОС Linux");
    if(isUnknown.checked)
        status_info.os.push("Машины, у которых неизвестна операционная система");

    if(is_inDomain.checked)
        status_info.domain.push("Машины, подключенные к домену");
    if(is_notDomain.checked)
        status_info.domain.push("Машины, не подключенные к домену");

    if(is_Active.checked)
        status_info.domain.push("Исключить машины не активные");
    if(is_notActive.checked)
        status_info.domain.push("Исключить активные машины");

    if(is_some_computer_types.checked){
        if(is_computer_type_ARM.checked)
            status_info.os.push("Машины, тип которых - АРМ");
        if(is_computer_type_server.checked)
            status_info.os.push("Машины, тип которых - сервер");
    }

    end_string = "";
    filter_count = 0;
    function draw_status(info){
        end_string += "<ul>"
        info.forEach(function(elem) {
            end_string += "<ol>" + elem + "</ol>"
            filter_count++;
        });
        end_string += "</ul>"
    }
    draw_status(status_info.dallas);
    draw_status(status_info.kaspersky);
    draw_status(status_info.os);
    draw_status(status_info.domain);
    if (filter_count)
        document.getElementById('filter_status').innerHTML = end_string;
    else
        document.getElementById('filter_status').innerHTML = "Сейчас не примененно ни одного фильтра";
    if(filter_count)
        if (filter_count == 1)
            filter_status_bar.value = "Активно " + filter_count + " фильтр";
        else
            filter_status_bar.value = "Активно " + filter_count + " фильтра";
    else
        filter_status_bar.value = "Активно 0 фильтров";
}
axios({
    url
    method
    withCredentials
    headers
}).then(function() {
});
axios({
    method : 'GET',
    url : 'api/get_computers/',
    withCredentials : true
}).then(function(res) {
    console.log(res.data.computers)
    var table = new Tabulator("#table", {
    data:res.data.computers,           //load row data from array
    layout:"fitColumns",      //fit columns to width of table
    tooltips:true,            //show tool tips on cells
    addRowPos:"top",          //when adding a new row, add it to the top of the table
    pagination:"local",       //paginate the data
    paginationSize:100,         //allow 7 rows per page of data
    initialSort:[             //set the initial sort order of the data
        {column:"name", dir:"asc"},
    ],
    dataFiltered : function(filters, rows) {
        table_pointer = this;
        setTimeout(function(){
            updateStatistic(table_pointer);
        }, 400)
    },
    // '#AED581' хороший цвет
    columns:[                 //define the table columns
        {title:"№", align:"center", formatter : "rownum", width:50, sorter:false, editor:false},
        {title:"Подразделение", field:"unit", align:"center", sorter:"string", width:75, headerFilter:"select", headerFilterParams:{values:true, verticalNavigation : "editor"}},
        {title:"КШ", field:"CG_name", align:"center", sorter:"string", width:75, headerFilter:"select", headerFilterParams:{values:true, verticalNavigation : "editor"}},
        {title:"Имя компьютера", field:"name", align:"center", sorter:"string", headerFilter:true},
        {title:"Дата создания в Active Direcotry", field:"ad", editor:false, align:"center", sorter:"date", sorterParams:{
            format : "YYYY-MM-DD",
            alignEmptyValues:"bottom"
        }, formatter:function(cell, formatterParams) {
            if( cell.getValue() == "Не зарегистрирован") {
                cell.getElement().style.backgroundColor = '#FCE4EC';
            }
            return cell.getValue();
        }},
        {title:"Активен в AD", field:"isActive", align:"center", formatter:"tickCross", width: 50},
        {title:"Dallas Lock", field:"dallas", editor: false, align:"center", formatter:function(cell) {
            if( cell.getValue() == "Отсутствует") {
                cell.getElement().style.backgroundColor = '#FCE4EC';
            } else if ( cell.getValue() == "Установлен" ){
                cell.getElement().style.backgroundColor = '#DCEDC8'
            } else {
                cell.getElement().style.backgroundColor = '#F0F4C3';
            }
            return cell.getValue();
        }},
        {title:"Агент Касперского", field:"kl_agent", align:"center", editor:false, formatter:function(cell){
            if( cell.getValue()  == good_agent_versions[0] ||
                cell.getValue()  == good_agent_versions[1] ||
                cell.getValue()  == good_agent_versions[2] ){
                cell.getElement().style.backgroundColor = '#DCEDC8';
            } else if ( cell.getValue() == "Отсутствует" ) {
                cell.getElement().style.backgroundColor = '#FCE4EC';
            } else {
                cell.getElement().style.backgroundColor = '#F0F4C3';
            }
            return cell.getValue()
        }},
        {title:"Защита Касперского", field:"kl_security", align:"center", editor:false, formatter:function(cell){
            if( cell.getValue() == good_security_versions[0] ||
                cell.getValue() == good_security_versions[1] ||
                cell.getValue() == good_security_versions[2] ||
                cell.getValue() == good_security_versions[3] ){
                cell.getElement().style.backgroundColor = '#DCEDC8';
            } else if (cell.getValue() == "Отсутствует") {
                cell.getElement().style.backgroundColor = '#FCE4EC';
            } else {
                cell.getElement().style.backgroundColor = '#F0F4C3';
            }
            return cell.getValue()
        }},
        {title:"IP в Касперском", field:"kl_ip", align:"center", headerFilter:true, editor:false, formatter:function(cell){
            if( cell.getValue() == "Неизвестно" ) {
                cell.getElement().style.backgroundColor = '#FCE4EC';
            }
            return cell.getValue()
        }},
        {title:"Есть дубликаты в KSC", field:"hasDuplicate", align:"center", formatter:"tickCross", width: 50},
        {title:"Операционная Система", field:"os", width:130, sorter:"string", align:"center", editor:false, formatter:function(cell){
            if( cell.getValue() == "Неизвестно" )
                cell.getElement().style.backgroundColor = '#FCE4EC';
            return cell.getValue()
        }},
        {title:"Последний вход", field:"loggined", width:100, align:"center", sorter:"date", sorterParams : {
            format:"YYYY-MM-DD",
            alignEmptyValues:"bottom"
        }, editor:false},
        {title:"Сервер DL", field:"dallas_server", sorter:"string", align:"center", width: 150},
        {title:"Тип устройства", field:"type", align : "center", editor:"select", editorParams:{values:{"1" :  "АРМ",
                                                                                      "2" : "Сервер",
                                                                                      "3" : "Управляемый коммутатор",
                                                                                      "4" : "Сетевой принтер",
                                                                                      "5" : "IP камера",
                                                                                      "6" : "ИБП"}},
                                                                formatter : function(cell) {
                                                                    if (cell.getValue() == 1) return "АРМ"
                                                                    if (cell.getValue() == 2) return "Сервер"
                                                                    if (cell.getValue() == 3) return "Управляемый коммутатор"
                                                                    if (cell.getValue() == 4) return "Сетевой принтер"
                                                                    if (cell.getValue() == 5) return "IP камера"
                                                                    if (cell.getValue() == 6) return "ИБП"
                                                                },
                                                                cellEdited: function(cell){
                                                                    dataToSend = {};
                                                                    row = cell.getRow();
                                                                    computername = row.getCell('name').getValue();
                                                                    axios({
                                                                        method : "POST",
                                                                        url : "api/table/computer/" + computername + "/type/" + cell.getValue(),
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
            computername = row.getCell('name').getValue();
            console.log(computername);
            dataToSend.comment = cell.getValue();
            axios({
                method : 'POST',
                url : 'api/table/computer/' + computername + '/comment/',
                data : dataToSend,
                withCredentials : true
            }).then(function() {
                console.log('all right');
            }).catch(function() {
                console.log("we have some troubles");
            });
        }},
        {formatter: function formatters_buttons_cell(cell, formatterParams) {
            if (user_isAdmin && cell.getData().isBlocking){
                let isLocked = cell.getData().isLocked
                let computername = cell.getData().name
                console.log(cell.getData().name)
                space = '<span> </span>'
                if (isLocked) {
                    unlock_button = '<input type="button" value="V" id="unlock_button_' + computername + '" class="block_item" onclick=unlock_computer("' + computername + '")>'
                    return unlock_button
                } else {
                    lock_button = '<input type="button" value="X" id="lock_button_' + computername + '" class="block_item" onclick=lock_computer("' + computername + '")>'
                    return lock_button + space + '<span>Разблокирован</span>'
                }
            }
        }, width:70}
    ]})

    function filtration() {
        table.clearFilter();

        // filter by operation system
        let filters = []
        if (isWindows.checked)
            filters.push({ field : 'os', type : '!=', value : 'Windows'})
        if (isLinux.checked)
            filters.push({ field : 'os', type : '!=', value : 'Linux'})
        if (isUnknown.checked)
            filters.push({ field : 'os', type : '!=', value : 'Неизвестно'})

        // filter by Dallas lock
        if (isGoodDL.checked) {
            filters.push({ field : 'dallas', type : '!=', value : "Установлен"})
        }
        if (isWithoutDL.checked) {
            filters.push({ field : 'dallas', type : '!=', value : "Отсутствует"})
        }
        if (isErrorDL.checked) {
            let subFilters = []
            subFilters.push({ field : 'dallas', type : '=', value : "Установлен"})
            subFilters.push({ field : 'dallas', type : '=', value : "Отсутствует"})
            filters.push(subFilters)
        }

        // filter by agent
        if (isGoodAgent.checked){
            filters.push({ field : 'kl_agent', type : '!=', value : good_agent_versions[0]});
            filters.push({ field : 'kl_agent', type : '!=', value : good_agent_versions[1]});
            filters.push({ field : 'kl_agent', type : '!=', value : good_agent_versions[2]});
        }
        if (isWithoutAgent.checked) {
            filters.push({ field : 'kl_agent', type : '!=', value : "Отсутствует" });
        }
        if (isErrorAgent.checked) {
            subFilters = []
            subFilters.push({ field : 'kl_agent', type : '=', value : good_agent_versions[0] });
            subFilters.push({ field : 'kl_agent', type : '=', value : good_agent_versions[1] });
            subFilters.push({ field : 'kl_agent', type : '=', value : good_agent_versions[2] });
            subFilters.push({ field : 'kl_agent', type : '=', value : "Отсутствует" });
            filters.push(subFilters)
        }

        // filter by security
        if (isGoodSecurity.checked){
            filters.push({ field : 'kl_security', type : '!=', value : good_security_versions[0]});
            filters.push({ field : 'kl_security', type : '!=', value : good_security_versions[1]});
            filters.push({ field : 'kl_security', type : '!=', value : good_security_versions[2]});
            filters.push({ field : 'kl_security', type : '!=', value : good_security_versions[3]});
        }
        if (isWithoutSecurity.checked) {
            filters.push({ field : 'kl_security', type : '!=', value : "Отсутствует" });
        }
        if (isErrorSecurity.checked) {
            subFilters = []
            subFilters.push({ field : 'kl_security', type : '=', value : good_security_versions[0] });
            subFilters.push({ field : 'kl_security', type : '=', value : good_security_versions[1] });
            subFilters.push({ field : 'kl_security', type : '=', value : good_security_versions[2] });
            subFilters.push({ field : 'kl_security', type : '=', value : good_security_versions[3] });
            subFilters.push({ field : 'kl_security', type : '=', value : "Отсутствует" });
            filters.push(subFilters)
        }

        if (is_inDomain.checked) {
            filters.push({ field : 'ad', type : '=', value : "Не зарегистрирован"});
        }

        if (is_notDomain.checked) {
            filters.push({ field : 'ad', type : '!=', value : "Не зарегистрирован"});
        }

        if (is_Active.checked) {
            filters.push({ field : 'isActive', type : '=', value : true});
        }

        if (is_notActive.checked) {
            filters.push({ field : 'isActive', type : '=', value : false});
        }

        if (is_some_computer_types.checked){
            if (is_computer_type_ARM.checked)
                filters.push({ field : 'type', type : '=', value : 1 })
            if (is_computer_type_server.checked)
                filters.push({ field : 'type', type : '=', value : 2 })
        }

        if (is_klIP.checked) {
            filters.push({ field : 'kl_ip', type : '!=', value : "Неизвестно"});
        }

        table.setFilter(filters);
        updateStatistic(table);
        updateFilterStatus();
    }
    set_filter_button.addEventListener('click', filtration);

    function clearMarks() {
        isGoodDL.checked = false
        isWithoutDL.checked = false
        isErrorDL.checked = false

        isGoodAgent.checked = false
        isGoodSecurity.checked = false
        isWithoutAgent.checked = false
        isWithoutSecurity.checked = false
        isErrorAgent.checked = false
        isErrorSecurity.checked = false
        is_klIP = false;

        isWindows.checked = false
        isLinux.checked = false
        isUnknown.checked = false

        is_inDomain.checked = false;
        is_notDomain.checked = false;

        is_Active.checked = false;
        is_notActive.checked = false;

        is_all_computer_types.checked = true;
        is_some_computer_types.checked = false
        is_computer_type_ARM.checked = false;
        is_computer_type_server.checked = false;
    }
    clear_filter_button.addEventListener('click', function() {
        clearMarks();
        table.getColumn("unit").setHeaderFilterValue("");
        table.getColumn("name").setHeaderFilterValue("");
        table.getColumn("kl_ip").setHeaderFilterValue("");
        table.clearFilter();
        updateFilterStatus();
    });

    open_filters_button.addEventListener('click', function() {
        if (macroses_block.hidden == false)
            macroses_block.hidden = true;
            open_macroses_button.value = "Открыть макросы";
        if(filter_block.hidden == true) {
            open_filters_button.value = "Закрыть фильтры";
            filter_block.hidden = false;
        } else {
            open_filters_button.value = "Открыть фильтры";
            filter_block.hidden = true;
        }
    });

    open_macroses_button.addEventListener('click', function() {
        if (filter_block.hidden == false)
            filter_block.hidden = true
            open_filters_button.value = "Открыть фильтры";
        if (macroses_block.hidden == true) {
            open_macroses_button.value = "Закрыть макросы";
            macroses_block.hidden = false;
        } else {
            open_macroses_button.value = "Открыть макросы";
            macroses_block.hidden = true;
        }
    });

    mc_without_agent.addEventListener('click', function() {
        clearMarks();
        isGoodAgent.checked = true;
        isErrorAgent.checked = true;
        is_Active.checked = true;
        filtration();
    });

    mc_without_security.addEventListener('click', function() {
        clearMarks();
        isGoodSecurity.checked = true;
        isErrorSecurity.checked = true;
        is_Active.checked = true;
        filtration();
    });

    mc_problems_kl.addEventListener('click', function() {
        clearMarks();
        isGoodAgent.checked = true;
        isWithoutAgent.checked = true;
        isGoodSecurity.checked = true;
        isWithoutSecurity.checked = true;
        is_Active.checked = true;
        filtration();
    });

    mc_without_dl.addEventListener('click', function() {
        clearMarks();
        isGoodDL.checked = true;
        isErrorDL.checked = true;
        is_Active.checked = true;
        is_some_computer_types.checked = true;
        is_computer_type_ARM.disabled = false;
        is_computer_type_server.disabled = false;
        is_computer_type_ARM.checked = true;
        isLinux.checked = true;
        isUnknown.checked = true;
        filtration();
    });

    mc_without_domain.addEventListener('click', function() {
        clearMarks();
        is_inDomain.checked = true;
        filtration();
    });

    mc_problems_dl.addEventListener('click', function() {
        clearMarks();
        isGoodDL.checked = true;
        isWithoutDL.checked = true;
        is_Active.checked = true;
        console.log(is_computer_type_ARM)
        console.log(is_computer_type_server)
        is_computer_type_ARM.disabled = false
        is_computer_type_server.disabled = false
        is_some_computer_types.checked = true;
        is_computer_type_ARM.checked = true;
        isLinux.checked = true;
        isUnknown.checked = true;
        filtration();
    });

    mc_isActive.addEventListener('click', function() {
        clearMarks();
        is_notDomain.checked = true;
        is_Active.checked = true;
        filtration();
    });

    mc_wrong_agent.addEventListener('click', function(){
        clearMarks();
        is_Active.checked = true;
        isGoodAgent.checked =true;
        isWithoutAgent.checked =true;
        isErrorSecurity.checked =true;
        filtration();
    });
    mc_wrong_security.addEventListener('click', function() {
        clearMarks();
        is_Active.checked = true;
        isGoodSecurity.checked =true;
        isWithoutSecurity.checked =true;
        isErrorAgent.checked =true;
        filtration();
    });

    download_button.addEventListener('click', function() {
        table.download("xlsx", "data.xlsx", {sheetName:"MyData"});
    });

    filter_status_bar.addEventListener('click', function() {
        filter_status.hidden = !filter_status.hidden;
    });

    updateStatistic(table);

    updated = new Date(res.data.last_updated)
    console.log(updated)
    inner_last_updated.innerHTML = (updated.getDate() > 9 ? ' ' : '0') + updated.getDate() + "."
                                    + ((parseInt(updated.getMonth())+1) > 9 ? '' : '0') + (parseInt(updated.getMonth())+1) + "."
                                    + updated.getFullYear() + " "
                                    + (updated.getHours() > 9 ? '' : '0') + updated.getHours() + ":"
                                    + (updated.getMinutes() > 9 ? '' : '0') + updated.getMinutes();
});

function click_on_all_types(event){
    is_computer_type_ARM.checked = false
    is_computer_type_server.checked = false
    is_computer_type_ARM.disabled = true
    is_computer_type_server.disabled = true
};
is_all_computer_types.addEventListener('change', click_on_all_types);
is_some_computer_types.addEventListener('change', function() {
    is_computer_type_ARM.disabled = false
    is_computer_type_server.disabled = false
});

is_all_computer_types.checked = true
click_on_all_types()