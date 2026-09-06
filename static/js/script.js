const resumeInput = document.getElementById("resume");


if (resumeInput) {

    resumeInput.addEventListener("change", function () {

        const uploadBox =
            document.querySelector(".upload-box");


        if (!uploadBox) {
            return;
        }


        const heading =
            uploadBox.querySelector("h3");

        const description =
            uploadBox.querySelector("p");

        const fileInfo =
            uploadBox.querySelector("span");


        if (this.files.length > 0) {

            const file =
                this.files[0];


            heading.textContent =
                file.name;


            description.textContent =
                "Resume selected successfully ✓";


            fileInfo.textContent =
                `${(
                    file.size / 1024 / 1024
                ).toFixed(2)} MB • PDF`;


            uploadBox.classList.add(
                "selected"
            );

        }

    });

}