
do_init();

function do_init() {
	s = new Slave("http://89.88.36.152:8080/_rest_/");
	$("#startBtn").click(function (event) {
		s.start();
	});
	$("#stopBtn").click(function (event) {
		s.stop();
	});
}


