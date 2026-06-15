const usuarioId = localStorage.getItem("usuario_id");
const usernameLogueado = localStorage.getItem("username");

$(async function() {

    if (localStorage.getItem("usuario_autenticado") !== "true" || !usuarioId) {
        window.location.href = "../login/login.html";
        return;
    }

    $("#profile-username").text(`@${usernameLogueado}`);
    
    await cargarMisPines();
});

async function cargarMisPines() {
    const $grid = $("#user-pin-grid");
    $grid.empty(); 

    try {
//peticion mediante jquery
        const pines = await $.ajax({
            url: `http://127.0.0.1:8000/api/v1/pins/user/${usuarioId}`,
            method: 'GET',
            dataType: 'json'
        });

        $("#pin-count").text(pines.length);

        if (pines.length === 0) {
            $grid.html(`<p style="color: var(--text-muted); text-align: center; width: 100%;">Aún no has publicado ninguna idea en Fyntasy.</p>`);
            return;
        }
//se agrega interacciòn con jquery
        $.each(pines, function(index, pin) {
            const rutaImagen = pin.source.startsWith("http") ? pin.source : `http://127.0.0.1:8000/${pin.source}`;

            const $card = $("<div>", { class: "pin-card" });
            
            $card.html(`
                <img src="${rutaImagen}" alt="${pin.titulo}" style="cursor: pointer;" onclick="location.href='../previsualizacion/previsualizacion.html?id=${pin.id}'">
                <div class="pin-info">
                    <h4>${pin.titulo}</h4>
                    <p>${pin.descripcion || 'Sin descripción.'}</p>
                </div>
            `);
            
            $grid.append($card);
        });

    } catch (error) {
        console.error("Error cargando galería del perfil", error);
    }
}