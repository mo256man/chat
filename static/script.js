var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
const userName = $("#user_name").text();

// 参加ボタン
$(".btn_join").on("click", function(){
    const id = $(this).attr("id");
    socket.emit("join_user", {"id":id, "user_name":userName});
});

// ゲームスタートボタン
$("#btn_start").on("click", function(){
    const admin = $("#admin_name").text();
    if (admin == userName) {
        socket.emit("game_start");
    }
});


// ページがロードされた時に参加者リストを要求する
window.onload = function() {
    socket.emit("join");
    socket.emit("get_users");
};

// 参加者リスト更新
socket.on("update_users", function(data) {
    for (let [key, value] of Object.entries(data)) {
        $("#" + key + "_name").text(value);
    }
    if (data["admin"]==userName) {
        $("#btn_start").removeClass("start_na");
        $("#btn_start").addClass("start_ok");
    } else {
        $("#btn_start").removeClass("start_ok");
        $("#btn_start").addClass("start_na");
    }
});

