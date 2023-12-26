// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

require(["jquery", "moment", "jhapi"], function ($, moment, JHAPI) {
  "use strict";

  var base_url = window.jhdata.base_url;
  var user = window.jhdata.user;
  var api = new JHAPI(base_url);
  $("#kill").hide();
  $("#save").hide();
  get_myserver_name().then((value)=>{
    document.getElementById("repository_name").value= value;
    $("#save").click(commitServer);
    $("#save").show();
  })

  // Named servers buttons

  function getRow(element) {
    while (!element.hasClass("home-server-row")) {
      element = element.parent();
    }
    return element;
  }

  function disableRow(row) {
    row.find(".btn").attr("disabled", true).off("click");
  }

  function enableRow(row, running) {
    // enable buttons on a server row
    // once the server is running or not
    row.find(".btn").attr("disabled", false);
    row.find(".stop-server").click(stopServer);
    row.find(".delete-server").click(deleteServer);

    if (running) {
      row.find(".start-server").addClass("hidden");
      row.find(".delete-server").addClass("hidden");
      row.find(".stop-server").removeClass("hidden");
      row.find(".server-link").removeClass("hidden");
    } else {
      row.find(".start-server").removeClass("hidden");
      row.find(".delete-server").removeClass("hidden");
      row.find(".stop-server").addClass("hidden");
      row.find(".server-link").addClass("hidden");
    }
  }


  function startServer() {
    var row = getRow($(this));
    var serverName = row.find(".new-server-name").val();
    if (serverName === "") {
      // ../spawn/user/ causes a 404, ../spawn/user redirects correctly to the default server
      window.location.href = "./spawn/" + user;
    } else {
      window.location.href = "./spawn/" + user + "/" + serverName;
    }
  }

  function stopServer() {
    var row = getRow($(this));
    var serverName = row.data("server-name");

    // before request
    disableRow(row);

    // request
    api.stop_named_server(user, serverName, {
      success: function () {
        enableRow(row, false);
      },
    });
  }

  function deleteServer() {
    var row = getRow($(this));
    var serverName = row.data("server-name");

    // before request
    disableRow(row);

    // request
    api.delete_named_server(user, serverName, {
      success: function () {
        row.remove();
      },
    });
  }
  async function killServer(){
    // APIエンドポイントのURLを組み立てる
  const apiUrl = "/api/container_kill";
  // fetch()メソッドでAPIを呼び出す
  const response = await fetch(apiUrl, {
        method: "GET",
        headers: {
            "Authorization": "token {{ user.api_tokens[0] }}"
        }
    });


    if (response.ok) {
        $("#repository_name").hide();
        $("#save").hide();
        $("#kill").hide()
        const data = await response.json();
        alert(data.message);
    } else {
        alert(`Error: ${response.status}`);
    }
  }
  async function commitServer(){
    // prefixのテキストを取得する
  const repository_name = document.getElementById("repository_name").value;
  if(repository_name == ""){
    alert("Error: You have to input repository_name")
    return
  };
  // APIエンドポイントのURLを組み立てる
  const apiUrl = "/api/image_commit?repository_name=" + encodeURIComponent(repository_name);
  // fetch()メソッドでAPIを呼び出す
  const response = await fetch(apiUrl, {
        method: "GET",
        headers: {
            "Authorization": "token {{ user.api_tokens[0] }}"
        }
    });

    if (response.ok) {
        const data = await response.json();
        alert(data.message);
    } else {
        alert(`Error: ${response.status}`);
    }
  }
  async function get_myserver_name(){
  // APIエンドポイントのURLを組み立てる
  const apiUrl = "/api/find_container_name";
  // fetch()メソッドでAPIを呼び出す
  const response = await fetch(apiUrl, {
        method: "GET",
        headers: {
            "Authorization": "token {{ user.api_tokens[0] }}"
        }
    });

    if (response.ok) {
        const data = await response.json();
        console.log(data)
        return data.image_name
    } else {
        return "my-docker/singleuser"
    }
  }
  async function get_container_stopped(){
  // APIエンドポイントのURLを組み立てる
  const apiUrl = "/api/find_container_name";
  // fetch()メソッドでAPIを呼び出す
  try{
  const response = await fetch(apiUrl, {
        method: "GET",
        headers: {
            "Authorization": "token {{ user.api_tokens[0] }}"
        }
    });

    if (response.ok) {
        const data = await response.json();
        console.log(data)
        return true
    } else {
        return false
    }
  }catch (error){
    return false
  }
  }

  // initial state: hook up click events
  $("#stop").click(function () {
    $("#start")
      .attr("disabled", true)
      .attr("title", "Your server is stopping")
      .click(function () {
        return false;
      });
    api.stop_server(user, {
      success: function () {
        $("#stop").hide();
        get_container_stopped().then((value)=>{
          console.log(value)
      if(value){
        $("#kill")
        .click(killServer)
        .show();
      }
      else{
        $("#repository_name").hide();
        $("#save").hide();
      }
        });
        
        $("#start")
          .text("Start My Server")
          .attr("title", "Start your default server")
          .attr("disabled", false)
          .attr("href", base_url + "spawn/" + user)
          .off("click");
      }
      });
    });


  $(".new-server-btn").click(startServer);
  $(".new-server-name").on("keypress", function (e) {
    if (e.which === 13) {
      startServer.call(this);
    }
  });

  $(".stop-server").click(stopServer);
  $(".delete-server").click(deleteServer);

  // render timestamps
  $(".time-col").map(function (i, el) {
    // convert ISO datestamps to nice momentjs ones
    el = $(el);
    var m = moment(new Date(el.text().trim()));
    el.text(m.isValid() ? m.fromNow() : "Never");
  });
});
