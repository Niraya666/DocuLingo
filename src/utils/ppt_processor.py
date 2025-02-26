import os

def convert_ppt_to_pdf(ppt_path, pdf_output_folder):
    if not os.path.exists(pdf_output_folder):
        os.makedirs(pdf_output_folder)

    convert_command = f'libreoffice --headless --convert-to pdf "{ppt_path}" --outdir "{pdf_output_folder}"'
    os.system(convert_command)

    generated_pdf = os.path.join(pdf_output_folder, os.path.splitext(os.path.basename(ppt_path))[0] + '.pdf')
    return generated_pdf

def convert_pdf_to_images(pdf_path, image_output_folder):
    if not os.path.exists(image_output_folder):
        os.makedirs(image_output_folder)

    convert_command = f'libreoffice --headless --convert-to png "{pdf_path}" --outdir "{image_output_folder}"'
    os.system(convert_command)

    generated_images = os.path.join(image_output_folder, os.path.splitext(os.path.basename(pdf_path))[0] + '.png')
    return generated_images

