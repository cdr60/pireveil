function change_alarm_type(id)
{
var obj=document.getElementById(id);
var aud=document.getElementById("play_audio");
var rad=document.getElementById("play_radio");
var bee=document.getElementById("play_beep");
if ((obj!="undefined") && (aud!="undefined") && (rad!="undefined") && (bee!="undefined"))
{
	var v=obj.value.toLowerCase();	
	if (v=="radio")
	{
		aud.style.display="none";
		rad.style.display="table-row";
		bee.style.display="none";
	}
	if (v=="fichier")
	{
		aud.style.display="table-row";
		rad.style.display="none";
		bee.style.display="none";
	}
	if (v=="beep")
	{
		aud.style.display="none";
		rad.style.display="none";
		bee.style.display="table-row";
	}
		
}

console.log(v);
}