document.addEventListener("DOMContentLoaded", function() {
  const doctorSelect = document.getElementById("doctor");
  const dateInput = document.getElementById("date");
  const timeSlotBox = document.getElementById("time-slot-box");
  const dateError = document.getElementById("date-error");
  const hiddenTimeSlotInput = document.getElementById("time_slot");
  function fetchTimeSlots() {
      const doctorId = doctorSelect.value;
      const appointmentDate = dateInput.value;
      if (doctorId && appointmentDate) {
          fetch(`/get_time_slots/?doctor=${doctorId}&date=${appointmentDate}`)
              .then(response => response.json())
              .then(data => {
                  timeSlotBox.innerHTML = "";
                  dateError.textContent = "";
                  hiddenTimeSlotInput.value = "";
                  if (data.error) {
                      dateError.textContent = data.error;
                  } else if (data.time_slots.length > 0) {
                      data.time_slots.forEach(slot => {
                          const button = document.createElement("div");
                          button.textContent = slot;
                          button.classList.add("time-slot-btn");
                          button.addEventListener("click", () => {
                              document.querySelectorAll(".time-slot-btn").forEach(btn => {
                                  btn.classList.remove("selected");
                              });
                              button.classList.add("selected");
                              hiddenTimeSlotInput.value = slot;
                          });
                          timeSlotBox.appendChild(button);
                      });
                  } else {
                      timeSlotBox.innerHTML = "<p>No available time slots for the selected date.</p>";
                  }
              })
              .catch(error => {
                  console.error("Error fetching time slots:", error);
                  dateError.textContent = "An error occurred while fetching time slots.";
              });
      } else {
          timeSlotBox.innerHTML = "";
      }
  }
  doctorSelect.addEventListener("change", fetchTimeSlots);
  dateInput.addEventListener("change", fetchTimeSlots);
});
