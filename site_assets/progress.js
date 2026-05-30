/** Course progress persisted in localStorage (static site). */
window.CourseProgress = (function () {
  const KEY = "orchestration-course-progress-v1";

  function load() {
    try {
      return JSON.parse(localStorage.getItem(KEY) || "{}");
    } catch {
      return {};
    }
  }

  function save(data) {
    localStorage.setItem(KEY, JSON.stringify(data));
  }

  function ensure(data) {
    if (!data.labs) data.labs = {};
    if (!data.exercises) data.exercises = {};
    return data;
  }

  function isLabDone(stem) {
    return !!ensure(load()).labs[stem];
  }

  function setLabDone(stem, done) {
    const data = ensure(load());
    if (done) data.labs[stem] = Date.now();
    else delete data.labs[stem];
    save(data);
  }

  function isExerciseDone(mod) {
    return !!ensure(load()).exercises[mod];
  }

  function setExerciseDone(mod, done) {
    const data = ensure(load());
    if (done) data.exercises[mod] = Date.now();
    else delete data.exercises[mod];
    save(data);
  }

  function summary(labStems, exerciseMods) {
    const data = ensure(load());
    const labsDone = labStems.filter((s) => data.labs[s]).length;
    const exDone = exerciseMods.filter((m) => data.exercises[m]).length;
    return {
      labsDone,
      labsTotal: labStems.length,
      exDone,
      exTotal: exerciseMods.length,
      complete: labsDone === labStems.length && exDone === exerciseMods.length,
    };
  }

  return { isLabDone, setLabDone, isExerciseDone, setExerciseDone, summary };
})();
