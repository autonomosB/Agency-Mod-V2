document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('analysisForm');
            const loadingOverlay = document.getElementById('loadingOverlay');
            const resultsContainer = document.getElementById('resultsContainer');
            const results = document.getElementById('results');
            const copyBtn = document.querySelector('.copy-btn');

            form.addEventListener('submit', async function(e) {
                        e.preventDefault();

                        // Mostrar loading y ocultar resultados anteriores
                        loadingOverlay.classList.remove('hidden');
                        resultsContainer.classList.add('hidden');
                        results.innerHTML = '';

                        // Obtener los valores del formulario
                        const brandTask = document.getElementById('brandTask').value;
                        const userTask = document.getElementById('userTask').value;

                        try {
                            const response = await fetch('/api/analyze', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    brandTask: brandTask,
                                    userTask: userTask
                                })
                            });

                            const data = await response.json();

                            if (!response.ok) {
                                throw new Error(data.error || 'Error en el servidor');
                            }

                            // Mostrar resultados
                            if (data.success && data.strategy) {
                                let html = '<div class="strategy-content">';

                                // Resumen
                                if (data.strategy.resumen) {
                                    html += `
                        <div class="strategy-section">
                            <h3><i class="fas fa-file-alt"></i> Resumen Ejecutivo</h3>
                            <div class="section-content">
                                <p>${data.strategy.resumen}</p>
                            </div>
                        </div>
                    `;
                                }

                                // Pasos
                                if (data.strategy.pasos && data.strategy.pasos.length > 0) {
                                    html += `
                        <div class="strategy-section">
                            <h3><i class="fas fa-tasks"></i> Plan de Acción</h3>
                            <div class="section-content">
                                <ul>
                                    ${data.strategy.pasos.map(paso => `<li>${paso}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    `;
                }

                // Recomendaciones
                if (data.strategy.recomendaciones && data.strategy.recomendaciones.length > 0) {
                    html += `
                        <div class="strategy-section">
                            <h3><i class="fas fa-lightbulb"></i> Recomendaciones Estratégicas</h3>
                            <div class="section-content">
                                <ul>
                                    ${data.strategy.recomendaciones.map(rec => `<li>${rec}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    `;
                }

                // Investigación
                if (data.strategy.investigacion && data.strategy.investigacion.length > 0) {
                    html += `
                        <div class="strategy-section">
                            <h3><i class="fas fa-search"></i> Investigación de Mercado</h3>
                            <div class="section-content">
                                <ul>
                                    ${data.strategy.investigacion.map(inv => `<li>${inv}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    `;
                }

                // Plan de medios
                if (data.strategy.plan_medios && data.strategy.plan_medios.length > 0) {
                    html += `
                        <div class="strategy-section">
                            <h3><i class="fas fa-bullhorn"></i> Plan de Medios</h3>
                            <div class="section-content">
                                <ul>
                                    ${data.strategy.plan_medios.map(plan => `<li>${plan}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    `;
                }

                // Contenido
                if (data.strategy.contenido && data.strategy.contenido.length > 0) {
                    html += `
                        <div class="strategy-section">
                            <h3><i class="fas fa-pen-fancy"></i> Contenido Propuesto</h3>
                            <div class="section-content">
                                <ul>
                                    ${data.strategy.contenido.map(cont => `<li>${cont}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    `;
                }

                html += '</div>';
                results.innerHTML = html;
                resultsContainer.classList.remove('hidden');
            }

        } catch (error) {
            console.error('Error:', error);
            results.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>Error: ${error.message}</p>
                </div>
            `;
            resultsContainer.classList.remove('hidden');
        } finally {
            // Ocultar loading
            loadingOverlay.classList.add('hidden');
        }
    });

    // Funcionalidad del botón de copiar
    if (copyBtn) {
        copyBtn.addEventListener('click', function() {
            const textToCopy = results.innerText;
            navigator.clipboard.writeText(textToCopy).then(function() {
                // Cambiar temporalmente el icono para dar feedback
                const icon = copyBtn.querySelector('i');
                icon.classList.remove('fa-copy');
                icon.classList.add('fa-check');
                setTimeout(() => {
                    icon.classList.remove('fa-check');
                    icon.classList.add('fa-copy');
                }, 2000);
            }).catch(function(err) {
                console.error('Error al copiar:', err);
            });
        });
    }
});