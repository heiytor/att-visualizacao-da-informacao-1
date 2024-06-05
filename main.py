import seaborn as sns
import pandas as pd
from typing import Tuple
from io import BytesIO
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import matplotlib.pyplot as plt
import sys
import os

class Graph:
    @staticmethod
    def write_buffer(data, kind: str, size: Tuple[int, int], title: str = "", x_label: str = "", y_label: str = "", autopct: str = ""):
        plt.figure(figsize=size)

        match kind:
            case "bar":
                data.plot(kind=kind)
            case "pie":
                data.plot(kind=kind, autopct=autopct)
            case _:
                raise TypeError("kind must be \"bar\" or \"pie\"")

        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)

        buffer = BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)

        plt.close()

        return buffer


class PDF:
    spacing_x = 50

    def __init__(self, pdf_path: str, name: str, rgm: str, institution: str, course: str, dataset_link: str, video_link: str, repo_link: str):
        self.c = canvas.Canvas(pdf_path, pagesize=letter)
        self.__create(name, rgm, institution, course, dataset_link, video_link, repo_link)

    def __create(self, name: str, rgm: str, institution: str, course: str, dataset_link: str, video_link: str, repo_link):
        # Draw header
        header_y = 750 
        header_spacing = 15 
        self.c.setFont("Helvetica-Bold", 12)
        self.c.drawString(50, header_y, f"Nome: {name}")
        self.c.drawString(50, header_y - header_spacing, f"RGM: {rgm}")
        self.c.drawString(50, header_y - (2 * header_spacing), f"GitHub: {repo_link}")
        self.c.drawString(50, header_y - (3 * header_spacing), f"Instituição: {institution}")
        self.c.drawString(50, header_y - (4 * header_spacing), f"Curso: {course}")

        # Draw links
        link_y = header_y - (4 * header_spacing)
        self.c.setFont("Helvetica", 10)
        self.c.drawString(50, link_y - header_spacing, f"Link do dataset utilizado: {dataset_link}")
        self.c.drawString(50, link_y - (2 * header_spacing), f"Link do meu video de apresentação: {video_link}")

    def write_string(self, content: str, x: int = 0, y: int = 0):
        if x == 0:
            x = self.spacing_x

        self.c.drawString(x, y, content)

    def write_buffer(self, buffer, x: int, y: int, width: int, height: int):
        self.c.drawImage(ImageReader(buffer), x, y, width, height)

    def save(self):
        self.c.save()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <pdf_name>")
        sys.exit(1)

    pdf_name = sys.argv[1]
    pdf = PDF(
        pdf_name,
        name="Heitor Danilo Silva Barros",
        rgm=os.environ.get("RGM", "N/A"),
        institution="Universidade Cidade São Paulo - UNICID",
        course="Ciências da Computação",
        dataset_link="https://drive.google.com/uc?id=1zO8ekHWx9U7mrbx_0Hoxxu6od7uxJqWw&export=download",
        video_link="placeholder",
        repo_link="https://github.com/heiytor/att-visualizacao-da-informacao-1",
    )

    df = pd.read_csv("dataset/customers.csv")
    df["Subscription Date"] = pd.to_datetime(df["Subscription Date"])
    df["Subscription Month"] = df["Subscription Date"].dt.month

    ##
    pdf.write_string("Histograma do número de assinaturas por mês.", y=635)

    buffer = Graph.write_buffer(
        df["Subscription Month"].value_counts().sort_index(),
        kind="bar", 
        size=(10, 6),
        title="Número de Assinaturas por Mês",
        x_label="Mês",
        y_label="Número de Assinaturas"
    )

    pdf.write_buffer(buffer, 50, 430, 350, 200)

    ##
    pdf.write_string("Distribuição dos clientes por empresa, mostrando as 5 maiores empresas e \"Outros\" para o resto.", y=410)

    company_distribution = df["Company"].value_counts()
    top_5_companies = company_distribution.nlargest(10)
    other_companies_sum = company_distribution.iloc[10:].sum()
    buffer = Graph.write_buffer(
        pd.concat([top_5_companies, pd.Series({"Outros": other_companies_sum})]),
        kind="pie",
        size=(10, 6),
        title="Distribuição dos Clientes por Empresa",
        autopct="%1.1f%%"
    )

    pdf.write_buffer(buffer, 50, 190, 350, 200)

    ## 
    pdf.write_string("Distribuição dos clientes por país, mostrando os 5 maiores países e \"Outros\" para o resto.", y=190)

    country_distribution = df["Country"].value_counts()
    top_5_countries = country_distribution.nlargest(5)
    other_countries_sum = country_distribution.iloc[5:].sum()
    buffer = Graph.write_buffer(
        pd.concat([top_5_countries, pd.Series({"Outros": other_countries_sum})]),
        kind="pie",
        size=(10, 6),
        title="Distribuição dos Clientes por País",
        autopct="%1.1f%%"
    )

    pdf.write_buffer(buffer, 50, -20, 350, 200)

    pdf.save()
