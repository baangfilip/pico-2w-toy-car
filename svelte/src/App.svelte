<script lang="ts">
  import Range from './lib/Range.svelte'
  let socket = new WebSocket('ws://' + location.host + '/ws');
  let value =  $state(0);

  $effect(() => {
		const id = setInterval(() => {
      if(socket.readyState == 1){
        socket.send(value);
      }
		}, 100);

		return () => {
			clearInterval(id);
		};
	});
  var wsStates = {
    0: "Connecting ⚠️",
    1: "Open ✔",
    2: "Closing ⚠️",
    3: "Closed ⚠️"
  }
</script>

<main>
  <div class="card">
    <div>
      Socket state: {wsStates[socket.readyState]}
      <br><br>
    </div>
	  <label for="basic-remote">Remote</label>
    <div class="slider">
      <Range on:change={(e) => value = e.detail.value} id="basic-remote"/>
    </div>
    <h3>
      {value}
    </h3>
  </div>
</main>

<style>
</style>
