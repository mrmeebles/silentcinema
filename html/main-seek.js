const audio1 = document.getElementById('audio1');
const audio2 = document.getElementById('audio2');
let sound = [audio1,audio2];
let active_player = 0;
let next_player = 1;
let last_event = 0;
let system_offset = 0;
let system_offset_history = [];
let eof_history = [];
let last_offset = 0;
let extra_offset = 0;
let active = false;
let debug = false;
let sync = -0.2;


function toggle_debug(){
	if (debug == false){
		debug = true;
		brightMoon();
	} else {
		debug = false;
		regularMoon();
	}
}

function get_next_player(){
	if (active_player == 0){
		return 1;
	} else {
		return 0;
	}
}

function clean_up(){
	console.log("Cleaning up...");
	eof_history = [];
	last_offset = 0;
	extra_offset = 0;
}

function update_playing_display(fileName){
	let parts = decodeURI(fileName).split("/");
	let last = parts[(parts.length - 1)].replace(".mp3","").replace(".m4a","").replaceAll("."," ");
	if ('mediaSession' in navigator) {
		navigator.mediaSession.metadata = new MediaMetadata({title: last});
	}
	setWaiting(last);
	if (active != true){
		showBigPLay();
	}
}

function get_standard_deviation(array) {
  const n = array.length;
  const mean = array.reduce((a, b) => a + b) / n;
  const stddev = Math.sqrt(array.map(x => Math.pow(x - mean, 2)).reduce((a, b) => a + b) / n);
  return [mean,stddev];
}

function check_system_offset(now_time){
	system_offset_history.push(now_time - (Date.now() / 1000));
	if (system_offset_history.length == 1){
		system_offset = system_offset_history[0];
		return;
	}
	if (system_offset_history.length > 20){
		system_offset_history.shift();
	}
	let vals = get_standard_deviation(system_offset_history);
	let new_array = [];
	for (const element of system_offset_history){
		if (Math.abs(element - vals[0]) > vals[1]){
//			console.log("Skipping system offset "+element);
		} else {
			new_array.push(element);
//			console.log("Adding system offset "+element);
		}
	}
	const n = new_array.length;
	system_offset = new_array.reduce((a, b) => a + b) / n;
	console.log('New system offset: '+system_offset)
}

function get_average_eof(est_eof){
	eof_history.push(est_eof);
	if (eof_history.length == 1){
		return est_eof;
	}

	if (eof_history.length > 50){
		eof_history.shift();
	}

	let vals = get_standard_deviation(eof_history);
	let new_array = [];
	for (const element of eof_history){
		if (Math.abs(element - vals[0]) > vals[1]){
//			console.log("Skipping eof offset "+element);
		} else {
			new_array.push(element);
//			console.log("Adding eof offset "+element);
		}
	}
	const l = new_array.length;
	avg_eof = new_array.reduce((a, b) => a + b) / l;
	// If we've seeked in the file, reset estimate
	if (Math.abs(avg_eof - est_eof) > 2){
		console.log("Seek detected, resetting eof history...")
		eof_history = [est_eof];
		avg_eof = est_eof;
	}
	console.log('Average eof: '+avg_eof);
	return avg_eof;
}

function set_position(duration,position,ref_time,est_eof){
	avg_eof = get_average_eof(est_eof);

	d = sound[active_player].duration;
	s = sound[active_player].currentTime;
	let n = Date.now() / 1000;
	local_eof = (d - s + n  + system_offset);
	offset = (d - s + n  + system_offset) - avg_eof + sync;
	tolerance = 0.3 - (eof_history.length / 250);
	local_position = d - local_eof - n;
	console.log("d: "+d+" s: "+s+" position: "+(duration*position)+" local: "+local_position+" (n-ref):"+(n-ref_time)+"local_eof: "+ local_eof);
	if (debug == true){
		setMessage("d: "+d+" s: "+s+" position: "+(duration*position)+" local: "+local_position+" (n-ref):"+(n-ref_time)+"local_eof: "+ local_eof);
	}
	if (Math.abs(offset) > tolerance){
		if ((last_offset != 0) && (Math.abs(last_offset) < 0.5) && (Math.abs(offset) < 0.5)){
			extra_offset = (last_offset + offset) / 2;
		}
		sound[active_player].currentTime = (s + offset + extra_offset);
		console.log("New position: "+(s + offset)+" Current: "+s+" offset: "+offset+" extra_offset: "+extra_offset);
//		if (debug == true){
//			setMessage("New position: "+(s + offset)+" Current: "+s+" offset: "+offset+" extra_offset: "+extra_offset);
//		}
		last_offset = offset;
	} else {
		console.log("No seek, offset: "+offset+" tolerance: "+tolerance+" extra_offset: "+extra_offset);
//		if (debug == true){
//			setMessage("No seek, offset: "+offset+" tolerance: "+tolerance+" extra_offset: "+extra_offset);
//		}
		last_offset = 0;
	}
}

function check_state(state,update_active=false){
	let playing = false;
	if ((!sound[active_player].paused) && (sound[active_player].duration > 0)){
		playing = true;
	} else {
		console.log("Paused: "+sound[active_player].paused+", duration: "+sound[active_player].duration)
	}
	if ((playing == true) && (active != true)){
		active = true;
		hideBigPLay();
	}
	if ((state == "playing") && (playing != true)) {
		console.log("Paused: "+sound[active_player].paused+" Duration: "+sound[active_player].duration+" State: "+state);
		sound[active_player].play();
	  	console.log("playing...");
		if ('mediaSession' in navigator) {
			navigator.mediaSession.playbackState = 'playing';
		}
	} else if ((state != "playing") && (playing == true)) {
		sound[active_player].pause();
		console.log("Pausing...");
		if ('mediaSession' in navigator) {
			navigator.mediaSession.playbackState = 'paused';
		}
	}
}

function new_audio(active,fileName,autoPlay = false,loop=false){
	clean_up();
	console.log("new audio: clearing previous file");
	sound[active].pause();
	sound[active].currentTime = 0;
	sound[active].src = "";
	sound[active].removeAttribute('src');
	sound[active].load();

	console.log("new audio: Updating file");
	sound[active].src = fileName;
	sound[active].load();
	sound[active].loop = loop;
	if ((autoPlay == true) || (loop == true)){
		sound[active].play();
	} else {
		sound[active].pause();
	}
}

function prequeue(file){
	next_player = get_next_player();
	if ((sound[0].src == file) || (sound[1].src == file)){
		console.log(file+" is already prequeued. Skipping...");
		return;
	}
	// prepare prequeue
	console.log("prequeue: clearing previous queue");
	sound[next_player].pause();
	sound[next_player].currentTime = 0;
	sound[next_player].src = "";
	sound[next_player].removeAttribute('src');
	sound[next_player].load();

	console.log("prequeue: Updating queue");
	sound[next_player].src = file;
	sound[next_player].load();
	sound[next_player].pause();
}

// connect to Mercure
const url = new URL(window.location.href.replace("8008","8009").replace("sync.html","").replace("index2.html","")+".well-known/mercure");
// add watch event
url.searchParams.append("topic", window.location.href.replace("8008","8009").replace("sync.html","").replace("index2.html","")+"status");
const eventSource = new EventSource(url,{withCredentials: true});
// The callback will be called every time an update is published
eventSource.onmessage = function (e) {
	//console.log(e);
	let data = JSON.parse(e["data"])
	console.log(data);
	// if we got a playing update
	if (("playing" in data) && (e["lastEventId"] != last_event)) {
		// check the clock is in sync
		if ("now_time" in data){
			check_system_offset(data['now_time']);
		}
		console.log(data["playing"]);
		update_playing_display(data["playing"]);
		last_event = e["lastEventId"];

		// if filename doesn't match playing file
		if (sound[active_player].src != data["playing"]){
			// check if file is prequeued
			next_player = get_next_player();
			if (sound[next_player].src == data["playing"]){
				console.log("Playing queued file, next: "+next_player);
				sound[active_player].pause();
				active_player = next_player;
				clean_up();
				sound[active_player].play();
			} else {
				// file isn't prequeued, so add it
				console.log("Nothing prequeued, loading new file...");
				new_audio(active_player,data["playing"],true,data["loop"]);
			}
		} else {
			console.log("Nothing to do...");
		}

		// Update the play time
		if ( ("duration" in data) && ("position" in data) && ("ref_time" in data) && ("est_eof" in data) && (sound.length > 0)) {
			set_position(data["duration"],data["position"],data["ref_time"],data["est_eof"]);
		}
		// Update play state, e.g. playing or pause
		if (("state" in data) && (sound.length > 0)){
			if (data["loop"] == true) {
				check_state("playing");
			} else {
				check_state(data["state"]);
			}
		}
	// We got a warning to preload the next file
	} else if (("next" in data) && (e["lastEventId"] != last_event)) {
		next_player = get_next_player();
		if (sound[next_player].src != data["next"]){
			d = sound[active_player].duration;
			s = sound[active_player].seek;
			time_till_next = d - s;

			if (time_till_next > 30) {
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
	console.log("Starting the show...")
	active = true;
	sound[0].play();
	sound[1].play();
	play_next = get_next_player();
	sound[play_next].pause();
	hideBigPLay();
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
