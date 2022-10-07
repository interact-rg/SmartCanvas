document.addEventListener("DOMContentLoaded", async function (event) {
    const clientFeed = document.getElementById("clientFeed");
    const serverFeed = document.getElementById("serverFeed");
    const canvas = document.getElementById("canvas");

    const socket = io.connect({ reconnection: false });

    socket.on("connect", () => {
      console.log("Connected");
    });

    socket.on("disconnect", () => {
      console.log("Disconnected");
    });

    socket.on("connect_error", (error) => {
      console.log("Connect error! " + error);
    });

    socket.on("connect_timeout", (error) => {
      console.log("Connect timeout! " + error);
    });

    socket.on("error", (error) => {
      console.log("Error! " + error);
    });

    socket.on("consume", (msg) => {
      var img = new Image;

      const serveFeedCtx = serverFeed.getContext("2d");
      img.onload = function(){
        serveFeedCtx.drawImage(img, 0, 0, canvas.width, canvas.height);
      };

      img.src = msg;
    });

    socket.on("update_ui_response", (msg) => {
      console.log(msg)
      var visibles = []
      //visible messages visible
      for (var key in msg){
        var html_item = document.getElementById(key);
        if (key != "hold_timer" && key != "countdown") {
          html_item.textContent = msg[key];
          visibles.push(key);
        }
        else if (key == "hold_timer") {
          html_item = document.getElementById("hold_progress");
          html_item.value = msg[key] * 100;
          if (msg[key] <= 0 || msg[key] >= 1) {
            html_item.style.visibility = 'hidden';
          }
          else {
            html_item.style.visibility = 'visible';
          }
        }
        else if (key == "countdown") {
          if (msg[key] == "0") {
            html_item = document.getElementById("countdown");
            html_item.style.visibility = "hidden";
          }
          else {
            html_item = document.getElementById("countdown");
            html_item.style.visibility = "visible";
            html_item = document.getElementById("countdown_value");
            html_item.textContent = msg[key]
          }
        }
      }
      console.log(visibles)
      //hidden messages invisible
      var childas = document.getElementById('ui').getElementsByTagName('a');
      for( var i=0; i< childas.length; i++ ) {
        var childa = childas[i];
        if (!visibles.includes(childa.id)) {
          if (key != "hold_timer") {
            html_item = document.getElementById(childa.id);
            try {
              html_item.textContent = null;
            } catch (error) {
              //console.log("error with", childa.id, error)
            }
          }
        }
      }
    });

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      let stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false,
      });
      clientFeed.srcObject = stream;

      canvas
        .getContext("2d")
        .drawImage(clientFeed, 0, 0, canvas.width, canvas.height);
      
      const FPS = 30;
      let interval = setInterval(() => {
        canvas
          .getContext("2d")
          .drawImage(clientFeed, 0, 0, canvas.width, canvas.height);
        const image_data_url = canvas.toDataURL("image/jpeg");
        socket.emit("produce", image_data_url)
      }, 1000/FPS);
    }

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      let interval = setInterval(() => {
        socket.emit("update_ui_request")
      }, 200);
    }
    
});