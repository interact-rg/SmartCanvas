document.addEventListener("DOMContentLoaded", async function (event) {
    const clientFeed = document.getElementById("clientFeed");
    const serverFeed = document.getElementById("serverFeed");
    const canvas = document.getElementById("canvas");
    var itemsResized = false;

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
    //Normal and fullscreen modes use the same logic for canvas
    if (page_identifier.textContent == "fullscreen_symbol" || page_identifier.textContent == "normal") {
        var server_feed_visible = false;
        var countdownStarted = false;
        socket.on("update_ui_response", (msg) => {
            console.log(msg);
            console.log("server feed visibile", server_feed_visible)
            var used_keys = [];
            for (var key in msg){
                if (key != "hold_timer" && key != "countdown") {
                  used_keys.push(key)
                  ui_element_div = document.getElementById(key);
                  ui_element_div.style.display = "block";
                  resizeItem(key)
                  if (key == "help_1" || key == "help_2") {
                    ui_element_div.children[1].textContent = msg[key];
                  }
                  else {
                    ui_element_div.children[0].textContent = msg[key];
                  }
                  //When image is showing, message for current filter is still sent -> manually disable it
                  if (used_keys.includes("image_showing_promote")  && key == "filter_name" ) {
                    ui_element_div.style.display = "none";
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
                  if (!countdownStarted) {
                    countdownStarted = true;
                  }
                }

                console.log("countrdownstarted", countdownStarted)
                console.log("in msg ", "countdown" in msg)
                console.log("msg len", Object.keys(msg).length)
                if (countdownStarted && Object.keys(msg).length == 1) {
                  console.log("making hidden")
                  var html_item = document.getElementById("countdown");
                  html_item.style.visibility = "hidden";
                  countdownStarted = false;
                }
                else if (key == "countdown" && countdownStarted && Object.keys(msg).length != 1) {
                  console.log("making visible")
                  var html_item = document.getElementById("countdown");
                  html_item.style.visibility = "visible";
                  html_item = document.getElementById("countdown_value");
                  html_item.textContent = msg[key]
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
            if (used_keys.includes("help_1") && server_feed_visible) {
              server_feed_visible = false
            }

            var serverfeed_su = document.getElementById("serverFeed");
            var clientfeed_su = document.getElementById("clientFeed");
            if (server_feed_visible) {
              clientfeed_su.style.display = "none";
              serverfeed_su.style.display = "block";
            }
            else {
              clientfeed_su.style.display = "block";
              serverfeed_su.style.display = "none";
            }
        });
        socket.on("imgage_processing_started", (msg) => {
            console.log("image processing started")
            var processing_element = document.getElementById("image_processing");
            processing_element.style.display = "block";
            server_feed_visible = true;
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
        dl_qr_img.src = "data:image/png;base64 ".concat(msg);
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
      
      const FPS = 10;
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
        console.log("text moving functions")
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
            processing_anim.style['transform'] = 'translate(80%,25%)';
        }

        //"Stretch" everything to fit window (TODO?: Redo in some more sensible way)
        if (document.getElementById("page_identifier").textContent == "fullscreen_symbol") {
          const widthZoom = getWidth() / (canvass.width + 20);
          const heightZoom = getHeight() / (canvass.height + 20);
          body.style.zoom = Math.min(widthZoom, heightZoom);
        }

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

    function resizeItem(item) {
      console.log("resizeItem called", item)
      
      const center_texts = ["idle_text_1", "idle_text_2", "gdpr_consent"]
      const custom_texts = ["help_1", "help_2", "filter_name", "take_new"]

      if (center_texts.includes(item)) {
        adjustCenterText(item)
      }
      else if (custom_texts.includes(item)) {
        adjustCustomText(item)
      }

      return (true);
    }

    //Handle text that should be horizontally centered
    function adjustCenterText(key) {
      const y_offsets = {
        "idle_text_1": 'px, 326px)',
        "idle_text_2": 'px, 380px)',
        "gdpr_consent": 'px, 326px)'
      }
      
      const temp_element = document.getElementById(key);
      const text_child = "#".concat(key, " > a:first-of-type");
      var w_info = parseInt(document.querySelector(text_child).getBoundingClientRect().width);
      var x_offset = ((1280 - w_info) / 2) - 15;
      //console.log("calculated", x_offset, "from", w_info, "for", key);
      temp_element.style['transform'] = 'translate('.concat(x_offset.toString(), y_offsets[key]);
    }

    //Handle special cases (the main UI)
    function adjustCustomText(key) {
      console.log("customtext", key)
      const offsets = {
        'help_1': 'px, 0px)',
        'help_2': 'px, 0px)',
        'filter_name': 'translate(0px, -85px)',
        'image_showing_promote': 'translate(0px, -50px)'
      }
      
      const temp_element = document.getElementById(key);

      //Handle texts that are supposed to be pinned to right side
      if (key == "help_1" || key == "help_2") {
        const text_child = "#".concat(key, " > a:first-of-type");
        var w_info = parseInt(document.querySelector(text_child).getBoundingClientRect().width);
        var x_offset = (1280 - w_info) - 15 - 40;
        temp_element.style['transform'] = 'translate('.concat(x_offset.toString(), offsets[key])
      }

      else {
        temp_element.style['transform'] = offsets[key]
      }
      
    }

    //Redo zooming on window size change
    addEventListener('resize', (event) => {
      if (document.getElementById("page_identifier").textContent == "fullscreen_symbol") {
        console.log("resizing");
        const canvass = document.getElementById("canvas");
        const widthZoom = getWidth() / (canvass.width + 20);
        const heightZoom = getHeight() / (canvass.height + 20);
        body.style.zoom = Math.min(widthZoom, heightZoom);
      }
    });
});