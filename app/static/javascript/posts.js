function toggle_modal(){
	var modal = document.getElementById('modal');
	var toggle = modal.getAttribute('is-active');
	if(toggle)
		modal.removeAttribute('is-active');
	else
		modal.setAttribute('is-active', true);
}
function insert_content(response){
	document.getElementById('modal-content').innerHtml = response;
	toggle_modal();
}
function get_content(hash){
	url = '/content?hash=' + hash;
	async_request(url, function(){insert_content()});
	
}
function crawl_posts(){
	console.log('beginning of crawl posts');
	var url = '/crawl';
	document.getElementById('crawl_link').innerHtml = '<span class="loader"></span>';
	async_request(url, function(){crawl_callback();})
}
function crawl_callback(){
	console.log("callback");
	var anchor = '<a href="#" onclick="crawl_posts()">Crawl</a>';
	document.getElementById('crawl_link').innerHtml = anchor;
}
function async_request(url, callback){
	var xmlhttp;
	xmlhttp = new XMLHttpRequest();
	xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            callback(this);
       }
    };
	xmlhttp.open("GET", url, true);
	xmlhttp.send();
}
