let sound = [];
let last_event = 0;
let system_offset = 0;
let system_offset_is_set = false;
let os_offset = 0;
let sync = 200;
let active = false;

function update_playing_next(fileName){
    let parts = decodeURI(fileName).split("/");
    let last = parts[(parts.length - 1)].replace(".mp3","").replace(".m4a","").replaceAll("."," ");
    setWaiting(last+"-±-");
    if ('mediaSession' in navigator) {
        navigator.mediaSession.metadata = new MediaMetadata({title: last});
    }
    if (active != true){
        showBigPLay();
    }
}

function change_sync(i){
    sync = sync * 1 + i * 1;
    setWaiting("New ");
    console.log("Set new sync: " + sync);
}

function set_sync(i){
    sync = i * 1;
    console.log("Set new sync: " + sync);
}

function new_audio(fileName,a = false){
    var s = new Howl({
        src: [fileName],
        preload: true,
        html5: true,
        autoplay: a
    });
    return s;
}

function set_position(duration,offset,ref_time){
    d = sound[0]["player"].duration();
    s = sound[0]["player"].seek();
    let n = Date.now() / 1000;
    position = offset * d + (n - ref_time) + (sync / 1000) + system_offset;
    if (Math.abs(position - s) < 0.1){
        sound[0]["player"].rate(1)
        return;
    } else if (Math.abs(position - s) < 0.5){
        rate = 1 + ((position - s) / 10)
        sound[0]["player"].rate(rate)
        console.log("New position: "+position+" Current: "+s+" new rate: "+rate);
        return;
    }
    sound[0]["player"].seek(position);
    sound[0]["player"].rate(1)
    console.log("New position: "+position+" Current: "+s+" new rate: 1");
}

function check_state(state,update_active=false){
    if (sound.length < 1){
        return;
    }
    let playing = sound[0]["player"].playing()
    if ((playing == true) &&(active != true)){
        active = true;
        hideBigPLay();
    }
    if ((state == "playing") && (playing != true)) {
        sound[0]["player"].play();
        if ('mediaSession' in navigator) {
            navigator.mediaSession.playbackState = 'playing';
        }
    } else if (state != "playing") {
        console.log("Pausing...");
        sound[0]["player"].pause();
        if ('mediaSession' in navigator) {
            navigator.mediaSession.playbackState = 'paused';
        }
    }
}

function prequeue(file){
    if ((sound.length == 1) && (sound[0]["fileName"] != file)){
        sound.push({"player":false,"fileName":""});
        sound[1]["player"] = new_audio(file);
        sound[1]["fileName"] = file;
        console.log("prequeue: Adding new player to queue");
    } else if ((sound.length > 1) && (sound[1]["fileName"] != file)){
        sound[1]["player"].unload();
        sound[1]["player"] = new_audio(file);
        sound[1]["fileName"] = file;
        console.log("prequeue: Updating queue");
    } else {
        console.log("prequeue: File already present");
    }
}

// initiate players
const player1 = document.getElementById('audio1');
const player2 = document.getElementById('audio2');
let player_select = 1;

// connect to Mercure
const url = new URL(window.location.href.replace("8008","8009").replace("sync.html","")+".well-known/mercure");
// add watch event
url.searchParams.append("topic", window.location.href.replace("8008","8009").replace("sync.html","")+"status");
const eventSource = new EventSource(url,{withCredentials: true});
// The callback will be called every time an update is published
eventSource.onmessage = function (e) {
    //console.log(e);
    let data = JSON.parse(e["data"])
    // if we got a playing update
    if (("playing" in data) && (e["lastEventId"] != last_event)) {
        // check the clock is in sync
        if (("now_time" in data) && (system_offset_is_set == false)){
            system_offset = (data['now_time'] + 0.05) - (Date.now() / 1000);
            system_offset_is_set = true;
            console.log('System offset: '+system_offset)
        }
        console.log(data["playing"]);
        update_playing_next(data["playing"]);
        last_event = e["lastEventId"];
        // if nothing is playing, create player
        if (sound.length == 0) {
            sound.push({"player":false,"fileName":""});
            sound[0]["player"] = new_audio(data["playing"],true);
            sound[0]["fileName"] = data["playing"];
            console.log("Created new player");
        // If there is one player, check if it's the right file
        } else if (sound[0]["fileName"] != data["playing"]) {
            // if prequeued
            console.log("fileName"+sound[0]["fileName"]);
            console.log("fileName"+data["playing"]);
            if ((sound.length > 1) && (sound[1]["fileName"] == data["playing"])){
                sound[0]["player"].unload();
                sound.shift(); // remove the first element
                sound[0]["player"].play();
                console.log("Using queued player");
            } else {
                sound[0]["player"].unload();
                sound[0]["player"] = new_audio(data["playing"], true);
                sound[0]["fileName"] = data["playing"];
                console.log("Replaced with new source");
            }
        } else {
            console.log("Nothing to do...");
        }

        // Update the play time
        if ( ("duration" in data) && ("position" in data) && ("ref_time" in data) && (sound.length > 0)) {
            set_position(data["duration"],data["position"],data["ref_time"]);
        }
        // Update play state, e.g. playing or pause
        if (("state" in data) && (sound.length > 0)){
            check_state(data["state"]);
        }
    // We got a warning to preload the next file
    } else if (("next" in data) && (e["lastEventId"] != last_event)) {
        // if no preload, create it
        if (sound.length == 0) {
            console.log("No player loaded, ignoring next");
        } else if (((sound.length > 1) && (sound[1]["fileName"] != data["next"])) || (sound.length == 1)){
            let d = sound[0]["player"].duration();
            let s = sound[0]["player"].seek();
            console.log("d-s");
            console.log(d-s);
            if ((d-s) > 30) {
                let rand = Math.random() * 20000;
                const myTimeout = setTimeout(prequeue.bind(null,data["next"]), rand);
                console.log("Loading prequeue with delay");
            } else {
                prequeue(data["next"]);
                console.log("Loading prequeue, no delay");
            }
        }
    } else if ("setSync" in data) {
        set_sync(data["setSync"])
    }
}

function startTheShow(){
    active = true;
    hideBigPLay();
}

function push_sync() {
    const body = new URLSearchParams({
        data: '{"setSync":'+sync+'}',
        id: "",
        type: "",
        retry: "",
        topic: window.location.href.replace("8008","8009").replace("sync.html","")+"status"
    });

    fetch(window.location.href.replace("8008","8009").replace("sync.html","")+".well-known/mercure", {
    method: 'POST',
    headers: {
        'authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJtZXJjdXJlIjp7InB1Ymxpc2giOlsiKiJdLCJzdWJzY3JpYmUiOlsiaHR0cHM6Ly9leGFtcGxlLmNvbS9teS1wcml2YXRlLXRvcGljIiwie3NjaGVtZX06Ly97K2hvc3R9L2RlbW8vYm9va3Mve2lkfS5qc29ubGQiLCIvLndlbGwta25vd24vbWVyY3VyZS9zdWJzY3JpcHRpb25zey90b3BpY317L3N1YnNjcmliZXJ9Il0sInBheWxvYWQiOnsidXNlciI6Imh0dHBzOi8vZXhhbXBsZS5jb20vdXNlcnMvZHVuZ2xhcyIsInJlbW90ZUFkZHIiOiIxMjcuMC4wLjEifX19.KKPIikwUzRuB3DTpVw6ajzwSChwFw5omBMmMcWKiDcM',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    },
    body: body
})
   .then(response => response.json())
   .then(response => console.log(JSON.stringify(response)))
}