var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var mysql = require("mysql");
var port = process.env.PORT || 5000;

/* Creating POOL MySQL connection.*/

var pool = mysql.createPool({
    connectionLimit: 1000000000,
    host: 'localhost', // localhost
    user: 'root', // root
    password: '', // password db
    database: 'server', // tfm
    debug: false
});

app.get('*', function (req, res) {
    res.send('bye :D', 404);
});

io.on('connect', function (socket) {
    console.log("A user is connected");
    socket.on('rank', function (page) {
        pool.query('SELECT *, (select COUNT(*) from users) as total from users ORDER BY CheeseCount DESC limit 20 OFFSET ' + ((page.page - 1) * 20), function (error, results, fields) {
            var users = [];
            if (error) throw error;
            results.forEach(user => {
                users.push([user.Username, user.nameID, user.CheeseCount, user.FirstCount, user.BootcampCount, user.ShamanSaves, user.HardModeSaves, user.DivineModeSaves, user.user_line_status]);
            });
            io.emit('receiveRanking', {
                'totalPage': Math.round(results[0].total / 20) ? Math.round(results[0].total / 20) : 1,
                'ranks': users // name tag cheese first bootcamps save-sahamn hard-mode divine-mode useronline
            });
        });
    });
});

http.listen(port, function () {
    console.log('listening on *:' + port);
});
