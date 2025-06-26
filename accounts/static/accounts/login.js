document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("login-form");
    const identifierInput = document.getElementById("identifier");
    const passwordInput = document.getElementById("password");
    const errorMessage = document.getElementById("error-message");
    const registerLink = document.getElementById("register-link");

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const identifier = identifierInput.value.trim();
        const password = passwordInput.value.trim();

        const formData = new FormData();
        formData.append("identifier", identifier);
        formData.append("password", password);

        fetch("/accounts/check-user/", {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            console.log("✅ Response:", data);
            errorMessage.style.display = "none";

            if (data.status === "success") {
                window.location.href = "/";
            } else if (data.status === "wrong_password") {
                errorMessage.textContent = "عذرًا اسم أو رقم المستخدم أو كلمة المرور غير صحيحة.";
                errorMessage.style.display = "block";
            } else if (data.status === "not_found" || data.status === "new") {
                errorMessage.textContent = "عذرًا اسم أو رقم المستخدم غير مسجل.";
                errorMessage.style.display = "block";
            } else if (data.status === "error") {
                alert("حدث خطأ: " + data.message);
            }
        })
        .catch(error => {
            console.error("❌ Error:", error);
            alert("حدث خطأ يرجى المحاولة لاحقًا.");
        });
    });

    registerLink.addEventListener("click", function (e) {
        e.preventDefault();
        const identifier = identifierInput.value.trim();

        if (!identifier) {
            errorMessage.textContent = "يرجى إدخال رقم الجوال أو اسم المستخدم أولاً.";
            errorMessage.style.display = "block";
            return;
        }

        const formData = new FormData();
        formData.append("identifier", identifier);

        fetch("/accounts/check-user/", {
            method: "POST",
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            console.log("✅ Register Check:", data);
            if (data.status === "new") {
                window.location.href = "/accounts/verify/";
            } else if (data.status === "exists" || data.status === "success") {
                errorMessage.textContent = "المستخدم مسجل مسبقًا، الرجاء تسجيل الدخول.";
                errorMessage.style.display = "block";
            } else if (data.status === "error") {
                alert("حدث خطأ: " + data.message);
            }
        })
        .catch(error => {
            console.error("❌ Error:", error);
            alert("حدث خطأ يرجى المحاولة لاحقًا.");
        });
    });
});
