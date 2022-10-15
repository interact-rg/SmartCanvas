document.addEventListener("DOMContentLoaded", async function (event) {
    const clientFeed = document.getElementById("clientFeed");
    const serverFeed = document.getElementById("serverFeed");
    const canvas = document.getElementById("canvas");
    const itemsResized = false;

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

    page_identifier = document.getElementById("page_identifier");
    //Normal mode:
    if (page_identifier.textContent == "normal") {
        console.log("Do normal site stuffs")
        //TODO: use 'diplay: none' instead of 'visibility: hidden' to make invisible items not take space (or preferably make this more like fullscreen mode)
        socket.on("update_ui_response", (msg) => {
            console.log(msg)
            var visibles = []
            //visible messages visible
            for (var key in msg){
              var html_item = document.getElementById(key);
              if (key != "hold_timer" && key != "countdown") {
                html_item.style.visibility = 'visible'
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
                  if (childa.id != "hold_timer") {
                      html_item = document.getElementById(childa.id);
                      console.log("setting inviisble", html_item.id)
                      try {
                          //html_item.textContent = null;
                          html_item.style.visibility = "hidden";
                      } catch (error) {
                          console.log("error with", childa.id, error)
                      }
                }
              }
            }
        });
    }
    //Original fullscreen mode, to be deleted
    else if (page_identifier.textContent == "fullscreen") {
        console.log("DO fs stuffs")
        socket.on("update_ui_response", (msg) => {
            console.log(msg);
            var msgs = [];
            for (var key in msg){
                if (key != "hold_timer" && key != "countdown" && key !="idle_text_1") {
                  msgs.push(msg[key]);
                }
                else if (key == "hold_timer") {
                  var html_item = document.getElementById("hold_progress");
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
                    var html_item = document.getElementById("countdown");
                    html_item.style.visibility = "hidden";
                  }
                  else {
                    var html_item = document.getElementById("countdown");
                    html_item.style.visibility = "visible";
                    html_item = document.getElementById("countdown_value");
                    html_item.textContent = msg[key]
                  }
                }
            }
            var children = document.getElementById("fs_ui").children;
            for (var i = 0; i < children.length; i++) {
              if (i <= msgs.length - 1) {
                children[i].textContent = msgs[i];
                children[i].style.display = 'block';
              }
              else {
                children[i].style.display = 'none';
              }
            }
        });
    }
    //Fullscreen with symbols instead of text (more logical system for showing/hiding UI elements)
    else if (page_identifier.textContent == "fullscreen_symbol") {
        socket.on("update_ui_response", (msg) => {
            console.log(msg);
            var used_keys = [];
            for (var key in msg){
                if (key != "hold_timer" && key != "countdown" && key !="idle_text_1") {
                  used_keys.push(key)
                  ui_element_div = document.getElementById(key);
                  ui_element_div.style.display = "block";
                  if (key == "filter_name" || key == "image_showing_promote") {
                    ui_element_div.children[0].textContent = msg[key];
                  }
                }
                else if (key == "hold_timer") {
                  var html_item = document.getElementById("hold_progress");
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
                    var html_item = document.getElementById("countdown");
                    html_item.style.visibility = "hidden";
                  }
                  else {
                    var html_item = document.getElementById("countdown");
                    html_item.style.visibility = "visible";
                    html_item = document.getElementById("countdown_value");
                    html_item.textContent = msg[key]
                  }
                }
            }
            var children = document.getElementById("fs_ui").children;
            var to_hide_element = null;
            console.log(used_keys)
            for (var i = 0; i < children.length; i++) {
              if (children[i].tagName == "DIV" && !(used_keys.includes(children[i].id)) && children[i].id != "image_processing") {
                if(children[i].id == "dl_qr_div" && !(used_keys.includes("image_showing_promote"))) {
                    to_hide_element = document.getElementById(children[i].id);
                    to_hide_element.style.display = "none";
                } else if (children[i].id != "dl_qr_div") {
                    to_hide_element = document.getElementById(children[i].id);
                    to_hide_element.style.display = "none";
                }
              }
            }
        });
        socket.on("imgage_processing_started", (msg) => {
            console.log("image processing started")
            var processing_element = document.getElementById("image_processing");
            processing_element.style.display = "block";
        });
        socket.on("imgage_processing_finished", (msg) => {
            console.log("image processing finished")
            var processing_element = document.getElementById("image_processing");
            processing_element.style.display = "none";

            //Request download link (TODO: make condinational based on wheter user allowed for saving)
            socket.emit("get_dl_link", "");
        });
    }
    
    socket.on("dl_qr", (msg) => {
        var dl_qr_div = document.getElementById("dl_qr_div");
        var dl_qr_img = document.getElementById("dl_qr_img");
        dl_qr_div.style.display = "block";
        dl_qr_img.src = "data:image/png;base64 ".concat(msg)
    });

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      let stream = await navigator.mediaDevices.getUserMedia({
        //480p will also work fine but other resolutions might cause unexpected behaviour
        video: {
            width: { ideal: 1280 },
            height: { ideal: 720 } 
        },
        audio: false,
      });
      clientFeed.srcObject = stream;

      canvas
        .getContext("2d")
        .drawImage(clientFeed, 0, 0, canvas.width, canvas.height);
      
      const FPS = 20;
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
        socket.emit("update_ui_request");
        socket.emit("check_image_processing");
      }, 200);
    }

    //Once camera is initialized, adjust offsets of UI items based on resolution (currently will only work at 720/480p but should probably somehow made automatic)
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia && !itemsResized) {
        const canvass = document.getElementById("canvas");
        const hold = document.getElementById("hold_progress");
        const ctr = document.getElementById("countdown_value");
        const processing_anim = document.getElementById("image_processing");
        if (canvass.width == 640 && canvas.height == 480) {
            console.log("setting UI to 480p")
            hold.style['transform'] = 'translate(140%,2800%)';
            ctr.style['transform'] = 'transform: translate(350%, 100%)';
            processing_anim.style['transform'] = 'translate(25%,25%)'
        }
        else if (canvass.width == 1280 && canvas.height == 720) {
            console.log("setting UI to 720p")
            hold.style['transform'] = 'translate(350%,4000%)';
            ctr.style['transform'] = 'translate(820%, 150%)';
            processing_anim.style['transform'] = 'translate(80%,25%)'
        }

        //"Stretch" everything to fit window (TODO?: Redo in some more sensible way)
        const widthZoom = getWidth() / (canvass.width + 20);
        const heightZoom = getHeight() / (canvass.height + 20);
        body.style.zoom = Math.min(widthZoom, heightZoom);
    }

    //Technically width/height should be the max of possible values but seems to work best with just clientHeight/clientWidth
    function getWidth() {
        return Math.max(
          //document.body.scrollWidth,
          //document.documentElement.scrollWidth,
          //document.body.offsetWidth,
          //document.documentElement.offsetWidth,
          document.documentElement.clientWidth
        );
    }
    function getHeight() {
        return Math.max(
          //document.body.scrollHeight,
          //document.documentElement.scrollHeight,
          //document.body.offsetHeight,
          //document.documentElement.offsetHeight,
          document.documentElement.clientHeight
        );
    }

    //Redo zooming on window size change
    addEventListener('resize', (event) => {
        console.log("resizing");
        const canvass = document.getElementById("canvas");
        const widthZoom = getWidth() / (canvass.width + 20);
        const heightZoom = getHeight() / (canvass.height + 20);
        body.style.zoom = Math.min(widthZoom, heightZoom);
    });
});