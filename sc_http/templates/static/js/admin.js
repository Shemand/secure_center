let update_button = document.getElementById('send_update_statistic')

update_button.addEventListener('click', function() {
    axios({
        method : 'POST',
        url : '/api/update_statistic',
        withCredentials : true
    }).then(function(res) {
        console.log(res.data)
    }).catch(function() {
    })
});

axios({
    method : 'GET',
    url : '/api/update_logs',
    withCredentials : true
}).then(function(res) {
    records = res.data;
    logs_window = document.getElementById("logs")
    logs_window.innerHTML = ""
    records.forEach(function(element) {
        tmp_date = new Date(element.date)
        date = {
            year : tmp_date.getFullYear(),
            month : tmp_date.getMonth() + 1,
            day : tmp_date.getDate(),
            hours : tmp_date.getHours(),
            minutes : tmp_date.getMinutes(),
            seconds : tmp_date.getSeconds()
        }
        date_string = ((date.day > 9) ? "" : "0") + date.day + "." + ((date.month > 9) ? "" : "0") + date.month + "." + date.year;
        time_string = ((date.hours > 9) ? "" : "0") + date.hours + ":" + ((date.minutes > 9) ? "" : "0") + date.minutes + ":" + ((date.seconds > 9) ? "" : "0") + date.seconds
        logs_window.innerHTML = logs_window.innerHTML + "<span>" + "[" + date_string + " | " + time_string + "]" + ": " + element.text + "<br></span>"
    });
}).catch(function() {
    console.log("Imposible take logs data");
});