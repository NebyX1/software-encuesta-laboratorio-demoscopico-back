import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { surveySchema } from '../form/surveySchema';
import usePersistForm from '../store/usePersistForm';
import { useNavigate } from 'react-router';
import QuestionBlock from '../components/QuestionBlock';
import useSurveyCompleted from '../store/useSurveyCompleted'; // Importar el hook

const Form = () => {
  const navigate = useNavigate();
  const { formData, updateFormData, clearFormData } = usePersistForm();
  const { markCompleted } = useSurveyCompleted(); // Obtener la función para marcar como completado

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
    reset,
  } = useForm({
    resolver: zodResolver(surveySchema),
  });

  const watchedFields = watch();

  useEffect(() => {
    const isInitialized = Object.keys(watchedFields).length > 0;
    if (isInitialized && JSON.stringify(watchedFields) !== JSON.stringify(formData)) {
      updateFormData(watchedFields);
    }
  }, [watchedFields, updateFormData, formData]);

  useEffect(() => {
    if (Object.keys(formData).length > 0) {
      reset(formData);
    }
  }, [reset, formData]);

  const onSubmit = async (data) => { // Make the function async
    console.log('Original Form Data:', data);

    let ipAddress = 'N/A (Error fetching)'; // Default/error value

    // --- Fetch IP Address from ipify ---
    try {
      const response = await fetch('https://api.ipify.org?format=json');
      if (!response.ok) {
        throw new Error('Network response was not ok getting IP');
      }
      const ipData = await response.json();
      ipAddress = ipData.ip;
    } catch (error) {
      console.error("Could not fetch IP address:", error);
      // ipAddress remains 'N/A (Error fetching)'
    }
    // --- End Fetch IP Address ---

    // --- Add additional info ---
    const submissionTimestamp = new Date().toISOString();
    const userAgent = navigator.userAgent || navigator.vendor || window.opera;
    let deviceType = 'desktop';
    if (/android/i.test(userAgent) || (/iPad|iPhone|iPod/.test(userAgent) && !window.MSStream)) {
      deviceType = 'mobile';
    }

    const dataToSave = {
      ...data,
      submissionTimestamp,
      deviceType,
      ipAddress, // Include the fetched IP address
    };

    console.log('Data to Save:', dataToSave);

    // --- Start Download Logic ---
    const jsonData = JSON.stringify(dataToSave, null, 2);
    const blob = new Blob([jsonData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    const timestamp = submissionTimestamp.replace(/[:.]/g, '-');
    link.download = `survey-response-${timestamp}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    // --- End Download Logic ---

    clearFormData();
    markCompleted(); // Marcar la encuesta como completada
    navigate('/done');
  };

  return (
    <div className="bg-base-100 p-6 rounded-lg shadow-md max-w-2xl mx-auto mt-10 mb-10 overflow-hidden">
      <h1 className="text-3xl font-semibold mb-8">Encuesta Lavalleja Abril 2025</h1>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-10">
        <QuestionBlock>
          <div>
            <p className="text-lg font-medium mb-4">1. ¿Con cuál de los siguientes géneros te identificás?</p>
            <div className="flex flex-col gap-2">
              {['Femenino', 'Masculino'].map((opt, i) => (
                <label key={i} className="flex items-center gap-3">
                  <input
                    type="radio"
                    {...register('genero')}
                    value={opt}
                    className={`radio radio-primary ${errors.genero ? 'radio-error' : ''}`}
                  />
                  <span>{opt}</span>
                </label>
              ))}
            </div>
            {errors.genero && <p className="text-error text-sm mt-2">{errors.genero.message}</p>}
          </div>
        </QuestionBlock>

        <QuestionBlock>
          <div>
            <p className="text-lg font-medium mb-4">2. ¿En qué localidad de Lavalleja tenés tu credencial cívica radicada?</p>
            <div className="flex flex-col gap-2">
              {[
                'Minas',
                'José Pedro Varela',
                'Solis',
                'Batlle y Ordóñez',
                'Mariscala',
                'Otra zona urbana',
                'Otra zona rural',
              ].map((opt, i) => (
                <label key={i} className="flex items-center gap-3">
                  <input
                    type="radio"
                    {...register('localidad')}
                    value={opt}
                    className={`radio radio-primary ${errors.localidad ? 'radio-error' : ''}`}
                  />
                  <span>{opt}</span>
                </label>
              ))}
            </div>
            {errors.localidad && <p className="text-error text-sm mt-2">{errors.localidad.message}</p>}
          </div>
        </QuestionBlock>

        <QuestionBlock>
          <div>
            <p className="text-lg font-medium mb-4">3. ¿Dentro de qué rango etario te encontrás?</p>
            <div className="flex flex-col gap-2">
              {[
                'Entre 18 a 22 años',
                'Entre 23 a 35 años',
                'Entre 36 a 45 años',
                'Entre 46 a 55 años',
                'Entre 56 y 65 años',
                'De 66 o más años',
              ].map((opt, i) => (
                <label key={i} className="flex items-center gap-3">
                  <input
                    type="radio"
                    {...register('edad')}
                    value={opt}
                    className={`radio radio-primary ${errors.edad ? 'radio-error' : ''}`}
                  />
                  <span>{opt}</span>
                </label>
              ))}
            </div>
            {errors.edad && <p className="text-error text-sm mt-2">{errors.edad.message}</p>}
          </div>
        </QuestionBlock>

        <QuestionBlock>
          <div>
            <p className="text-lg font-medium mb-4">4. Si las elecciones Departamentales fueran el próximo domingo, ¿a cuál de los siguientes candidatos votarías?</p>
            <div className="flex flex-col gap-2">
              {[
                'Carol Aviaga / Partido Nacional',
                'Luis Carrese / Partido Colorado',
                'Daniel Ximénez / Frente Amplio',
                'Robert Bouvier / Partido Colorado',
                'Javier Umpierrez / Frente Amplio',
                'Mario García / Partido Nacional',
                'Partido Colorado / No he decidido candidato',
                'Frente Amplio / No he decidido candidato',
                'Partido Nacional / No he decidido candidato/a',
                'Sergio Charquero / Unidad Popular',
                'No he decidido',
                'No votaré/En blanco/Anulado',
                'Otra',
              ].map((opt, i) => (
                <label key={i} className="flex items-center gap-3">
                  <input
                    type="radio"
                    {...register('intendente')}
                    value={opt}
                    className={`radio radio-primary ${errors.intendente ? 'radio-error' : ''}`}
                  />
                  <span>{opt}</span>
                </label>
              ))}
            </div>
            {errors.intendente && <p className="text-error text-sm mt-2">{errors.intendente.message}</p>}
          </div>
        </QuestionBlock>

        <QuestionBlock>
          <div>
            <p className="text-lg font-medium mb-4">5. ¿Recordás a quién votaste en la segunda elección presidencial de Noviembre de 2024?</p>
            <div className="flex flex-col gap-2">
              {[
                'Delgado - Ripoll',
                'Orsi - Cosse',
                'No recuerdo',
                'Blanco / Anulado',
                'No voté',
              ].map((opt, i) => (
                <label key={i} className="flex items-center gap-3">
                  <input
                    type="radio"
                    {...register('balotaje')}
                    value={opt}
                    className={`radio radio-primary ${errors.balotaje ? 'radio-error' : ''}`}
                  />
                  <span>{opt}</span>
                </label>
              ))}
            </div>
            {errors.balotaje && <p className="text-error text-sm mt-2">{errors.balotaje.message}</p>}
          </div>
        </QuestionBlock>

        <QuestionBlock>
          <div>
            <p className="text-lg font-medium mb-4">6. Más allá de tus preferencias políticas, ¿con cuál de las siguientes frases estás más de acuerdo?</p>
            <div className="flex flex-col gap-2">
              {[
                'Lavalleja está estancada, necesita un cambio de dirección urgente.',
                'Lavalleja está en crecimiento, necesita seguir este camino actual.',
                'No lo sé',
              ].map((opt, i) => (
                <label key={i} className="flex items-center gap-3">
                  <input
                    type="radio"
                    {...register('estado')}
                    value={opt}
                    className={`radio radio-primary ${errors.estado ? 'radio-error' : ''}`}
                  />
                  <span>{opt}</span>
                </label>
              ))}
            </div>
            {errors.estado && <p className="text-error text-sm mt-2">{errors.estado.message}</p>}
          </div>
        </QuestionBlock>

        <QuestionBlock>
          <div>
            <p className="text-lg font-medium mb-4">7. ¿De las siguientes opciones con cuál concordás?</p>
            <div className="flex flex-col gap-2">
              {[
                'Para mí lo más importante es que el próximo intendente sea de mi partido político.',
                'Yo valoro a las personas antes que los partidos, quiero que el próximo intendente sea una buena persona.',
                'No lo sé',
              ].map((opt, i) => (
                <label key={i} className="flex items-center gap-3">
                  <input
                    type="radio"
                    {...register('partido_vs_persona')}
                    value={opt}
                    className={`radio radio-primary ${errors.partido_vs_persona ? 'radio-error' : ''}`}
                  />
                  <span>{opt}</span>
                </label>
              ))}
            </div>
            {errors.partido_vs_persona && <p className="text-error text-sm mt-2">{errors.partido_vs_persona.message}</p>}
          </div>
        </QuestionBlock>

        <QuestionBlock>
          <div>
            <p className="text-lg font-medium mb-4">8. ¿Qué percepción te genera Mario García?</p>
            <div className="flex flex-col gap-2">
              {[
                'Confianza',
                'Desilusión',
                'Indiferencia',
                'Esperanza',
                'Enojo',
                'Duda',
                'No lo sé',
              ].map((opt, i) => (
                <label key={i} className="flex items-center gap-3">
                  <input
                    type="radio"
                    {...register('percepcion_mario')}
                    value={opt}
                    className={`radio radio-primary ${errors.percepcion_mario ? 'radio-error' : ''}`}
                  />
                  <span>{opt}</span>
                </label>
              ))}
            </div>
            {errors.percepcion_mario && <p className="text-error text-sm mt-2">{errors.percepcion_mario.message}</p>}
          </div>
        </QuestionBlock>

        <QuestionBlock>
          <div>
            <p className="text-lg font-medium mb-4">9. ¿Qué percepción te genera Daniel Ximénez?</p>
            <div className="flex flex-col gap-2">
              {[
                'Confianza',
                'Curiosidad',
                'Duda',
                'Esperanza',
                'Indiferencia',
                'Enojo',
                'No lo sé',
              ].map((opt, i) => (
                <label key={i} className="flex items-center gap-3">
                  <input
                    type="radio"
                    {...register('percepcion_daniel')}
                    value={opt}
                    className={`radio radio-primary ${errors.percepcion_daniel ? 'radio-error' : ''}`}
                  />
                  <span>{opt}</span>
                </label>
              ))}
            </div>
            {errors.percepcion_daniel && <p className="text-error text-sm mt-2">{errors.percepcion_daniel.message}</p>}
          </div>
        </QuestionBlock>

        <QuestionBlock>
          <div>
            <p className="text-lg font-medium mb-4">10. ¿Cuál te parece la principal problemática de Lavalleja?</p>
            <div className="flex flex-col gap-2">
              {[
                'Falta de Empleo / Economía',
                'Salud',
                'Vivienda',
                'Seguridad Pública',
                'Oportunidades Educativas',
                'Oportunidades Deportivas',
                'Lavalleja necesita mejores gobernantes',
                'Otros',
                'En Lavalleja no hay ningún problema',
              ].map((opt, i) => (
                <label key={i} className="flex items-center gap-3">
                  <input
                    type="radio"
                    {...register('problemas')}
                    value={opt}
                    className={`radio radio-primary ${errors.problemas ? 'radio-error' : ''}`}
                  />
                  <span>{opt}</span>
                </label>
              ))}
            </div>
            {errors.problemas && <p className="text-error text-sm mt-2">{errors.problemas.message}</p>}
          </div>
        </QuestionBlock>

        <QuestionBlock>
          <div>
            <p className="text-lg font-medium mb-4">11. De las siguientes frases que refieren a la necesidad de mayor transparencia en el gobierno departamental, ¿con cuál estás más de acuerdo?</p>
            <div className="flex flex-col gap-2">
              {[
                'La Intendencia de Lavalleja necesita una auditoría para saber si el dinero de nuestros impuestos se ha venido administrando de forma adecuada o por el contrario se ha administrado de forma irresponsable.',
                'No es necesaria ninguna auditoría, yo confío en que se ha estado administrando bien.',
                'No lo sé',
              ].map((opt, i) => (
                <label key={i} className="flex items-center gap-3">
                  <input
                    type="radio"
                    {...register('auditoria')}
                    value={opt}
                    className={`radio radio-primary ${errors.auditoria ? 'radio-error' : ''}`}
                  />
                  <span>{opt}</span>
                </label>
              ))}
            </div>
            {errors.auditoria && <p className="text-error text-sm mt-2">{errors.auditoria.message}</p>}
          </div>
        </QuestionBlock>

        <QuestionBlock>
          <div>
            <p className="text-lg font-medium mb-4">12. Para completar esta encuesta, por favor ingresá un número válido de teléfono celular. De lo contrario, tu respuesta no será tenida en cuenta.</p>
            <input
              type="text"
              placeholder="099123456"
              {...register('telefono')}
              className={`input input-bordered w-full max-w-xs ${errors.telefono ? 'input-error' : ''}`}
            />
            {errors.telefono && <p className="text-error text-sm mt-2">{errors.telefono.message}</p>}
          </div>
        </QuestionBlock>

        <QuestionBlock>
          <button
            type="submit"
            className="btn btn-info text-base px-6 py-3 rounded-xl shadow-sm hover:shadow-md transition-all duration-200"
          >
            Enviar encuesta
          </button>
        </QuestionBlock>
      </form>
    </div>
  );
};

export default Form;