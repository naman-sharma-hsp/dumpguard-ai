document.addEventListener("DOMContentLoaded", () => {

  /* ---------------- MAP INIT ---------------- */

  const map = L.map("risk-map").setView([28.715, 77.312], 14);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap contributors"
  }).addTo(map);

  // IMPORTANT: force map to calculate size
  setTimeout(() => {
    map.invalidateSize();
  }, 200);

  /* ---------------- CHART INIT ---------------- */

  const ctx = document.getElementById("complaintChart").getContext("2d");

  const complaintChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: [],
      datasets: [{
        label: "Complaints",
        data: [],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false
    }
  });

  /* ---------------- FETCH DATA ---------------- */

  fetch("http://127.0.0.1:5000/results")
    .then(res => res.json())
    .then(data => {

      data.forEach(area => {

        // safety check
        if (!area.latitude || !area.longitude) return;

        let color = "green";
        if (area.risk_level === "High") color = "red";
        else if (area.risk_level === "Medium") color = "orange";

        // USE CIRCLE (NOT CIRCLEMARKER)
        L.circle(
          [Number(area.latitude), Number(area.longitude)],
          {
            radius: 50,
            color: color,
            fillColor: color,
            fillOpacity: 0.6
          }
        )
        .addTo(map)
        .bindPopup(`
          <b>Area ${area.area_id}</b><br>
          Risk: ${area.risk_level}<br>
          Complaints: ${area.complaint_count}
        `);
      });

      // Chart data
      complaintChart.data.labels = data.map(a => a.area_id);
      complaintChart.data.datasets[0].data = data.map(a => a.complaint_count);
      complaintChart.update();

    })
    .catch(err => {
      console.error("Dashboard fetch error:", err);
    });

});
