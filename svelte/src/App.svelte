<script lang="ts">
    import Range from './lib/Range.svelte'
    const host = location.host; 
    let socket = new WebSocket('ws://'+host+'/ws')
    let value = $state(0)
    let readyState = $state(0);
    let errorMessage = $state("");
    let voltage = $state(0);
    socket.onopen = (event) => { 
        heartbeat();
        requestVoltage();
        readyState = socket.readyState;
    }
    socket.onclose = (event) => { 
        readyState = socket.readyState;
        errorMessage = "reload browser";
    }
    socket.onerror = (event) => { 
        readyState = socket.readyState;
        errorMessage = "reload browser";
    }
    socket.onmessage = (event) => {
        if(event.data.indexOf("voltage:") === 0){
            setTimeout(() => {requestVoltage()}, 5000);
            voltage = event.data.split(":")[1];
        }else{ 
            heartbeat();
        }
    }
    function requestVoltage(){
        socket.send("volt");
    }
    let pingTimeout: any;
    function heartbeat() {
        clearTimeout(pingTimeout);
        
        pingTimeout = setTimeout(() => {
            console.log("close socket, no answer..")
            socket.close();
            readyState = socket.readyState;
            errorMessage = "reload browser";
        }, 5000);
        setTimeout(() => {socket.send("ping");}, 2000);
    }
    $effect(() => {
        const id = setInterval(() => {
            if (socket.readyState == 1) {
                socket.send(value)
            }
        }, 100)

        return () => {
            clearInterval(id)
        }
    })
    var wsStates = {
        0: 'Connecting 🚧',
        1: 'Open ✅',
        2: 'Closing 🚧',
        3: 'Closed 🚧',
    }
    function turnOnBlinkyLights(){
        fetch(`http://${host}/lights/blink`)
            .then((response) => {
                if (!response.ok) {
                    errorMessage = `reload browser error ${response.status}`;
                }
            })
    }

    function turnOnRunningLights(){
        fetch(`http://${host}/lights/on`)
            .then((response) => {
                if (!response.ok) {
                    errorMessage = `reload browser error ${response.status}`;
                }
            })
    }
    function turnOffRunningLights(){
        fetch(`http://${host}/lights/off`)
            .then((response) => {
                if (!response.ok) {
                    errorMessage = `reload browser error ${response.status}`;
                }
            })
    }
</script>

<main>
    <div class="card">
        <div>
            Socket state: {wsStates[readyState]}<br />
            {errorMessage}
            <br />
            {#if voltage > 4}
            🔋
            {:else}
            🪫
            {/if}
            {voltage}v
            <br /><br />
        </div>
        <div>
            <button on:click={turnOnBlinkyLights}>Blink 🚨</button>
            <br/>
            <br/>
            <button on:click={turnOnRunningLights}>Lights on</button>
            <button on:click={turnOffRunningLights}>Lights off</button>
            <br/>
            <br/>
        </div>
        <label for="basic-remote">Remote 🚔</label>
        <div class="slider">
            <Range
                on:change={(e) => (value = e.detail.value)}
                id="basic-remote"
            />
        </div>
        <h3>
            {value}
        </h3>
    </div>
</main>

<style>
</style>
