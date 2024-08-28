from flask import Flask, render_template, request, jsonify
import gradio as gr
import os
import pandas as pd
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)

class GeminiChatbot:
    def __init__(self):
        self.init_gemini_chatbot()
        self.load_csv_data()

    def init_gemini_chatbot(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')

    def load_csv_data(self):
        self.data = pd.read_csv('ventas.csv')
        self.data['fecha'] = pd.to_datetime(self.data['fecha'])

    def search_csv(self, question):
        question = question.lower()

        # Venta más alta
        if "venta más alta" in question:
            max_sale = self.data.loc[self.data['precio'].idxmax()]
            return f"La venta más alta fue de ${max_sale['precio']:.2f} realizada por {max_sale['vendedor']} el {max_sale['fecha'].strftime('%d/%m/%Y')} por el producto {max_sale['producto']}."

        # Venta más baja
        if "venta más baja" in question:
            min_sale = self.data.loc[self.data['precio'].idxmin()]
            return f"La venta más baja fue de ${min_sale['precio']:.2f} realizada por {min_sale['vendedor']} el {min_sale['fecha'].strftime('%d/%m/%Y')} por el producto {min_sale['producto']}."

        # Vendedor del producto
        if "vendedor del producto" in question:
            product = question.split("producto ")[-1].strip("?").lower()
            vendedores = self.data[self.data['producto'].str.lower() == product]['vendedor'].unique()
            if len(vendedores) > 0:
                return f"Los vendedores del producto {product} son: {', '.join(vendedores)}."
            else:
                return f"No se encontró ningún vendedor para el producto {product}."

        # Ventas en una fecha específica
        if "ventas en" in question:
            date_str = question.split("ventas en ")[-1].strip("?")
            try:
                date = pd.to_datetime(date_str)
                sales_on_date = self.data[self.data['fecha'].dt.date == date.date()]
                if not sales_on_date.empty:
                    total_sales = sales_on_date['precio'].sum()
                    sales_count = len(sales_on_date)
                    sales_info = ', '.join([f"{row['producto']} por {row['vendedor']} (${row['precio']:.2f})" for _, row in sales_on_date.iterrows()])
                    return f"El {date.strftime('%d/%m/%Y')} hubo {sales_count} ventas por un total de ${total_sales:.2f}. Detalles: {sales_info}"
                else:
                    return f"No se encontraron ventas en la fecha {date.strftime('%d/%m/%Y')}."
            except:
                return "No pude entender la fecha. Por favor, proporciona la fecha en un formato claro (por ejemplo, DD/MM/YYYY)."

        # Promedio de venta
        if "promedio de venta" in question:
            average_sale = self.data['precio'].mean()
            return f"El promedio de venta es ${average_sale:.2f}."

        # Ventas por vendedor
        if "cuántas ventas realizó" in question or "ventas de" in question:
            vendedor = question.split("realizó ")[-1].split("de ")[-1].strip("?").lower()
            ventas_vendedor = self.data[self.data['vendedor'].str.lower() == vendedor]
            if not ventas_vendedor.empty:
                sales_count = len(ventas_vendedor)
                total_sales = ventas_vendedor['precio'].sum()
                return f"{vendedor.capitalize()} realizó {sales_count} ventas por un total de ${total_sales:.2f}."
            else:
                return f"No se encontraron ventas para el vendedor {vendedor}."

        # Total de ventas en un período
        if "total de ventas" in question:
            if "en" in question:
                date_str = question.split("ventas en ")[-1].strip("?")
                try:
                    date = pd.to_datetime(date_str)
                    total_sales = self.data[self.data['fecha'].dt.date == date.date()]['precio'].sum()
                    return f"El total de ventas el {date.strftime('%d/%m/%Y')} fue ${total_sales:.2f}."
                except:
                    return "No pude entender la fecha. Por favor, proporciona la fecha en un formato claro (por ejemplo, DD/MM/YYYY)."
            elif "entre" in question:
                dates = question.split("entre ")[-1].split(" y ")
                try:
                    start_date = pd.to_datetime(dates[0])
                    end_date = pd.to_datetime(dates[1])
                    sales_in_period = self.data[(self.data['fecha'].dt.date >= start_date.date()) & (self.data['fecha'].dt.date <= end_date.date())]
                    total_sales = sales_in_period['precio'].sum()
                    return f"El total de ventas entre {start_date.strftime('%d/%m/%Y')} y {end_date.strftime('%d/%m/%Y')} fue ${total_sales:.2f}."
                except:
                    return "No pude entender las fechas. Por favor, proporciona las fechas en un formato claro (por ejemplo, DD/MM/YYYY)."

        # Productos vendidos por un vendedor
        if "productos vendió" in question:
            vendedor = question.split("vendió ")[-1].strip("?").lower()
            products_sold = self.data[self.data['vendedor'].str.lower() == vendedor]['producto'].unique()
            if len(products_sold) > 0:
                return f"{vendedor.capitalize()} vendió los siguientes productos: {', '.join(products_sold)}."
            else:
                return f"No se encontraron productos vendidos por {vendedor}."

        # Mejor vendedor
        if "mejor vendedor" in question:
            ventas_por_vendedor = self.data.groupby('vendedor')['precio'].sum().sort_values(ascending=False)
            mejor_vendedor = ventas_por_vendedor.index[0]
            total_ventas = ventas_por_vendedor.iloc[0]
            return f"El mejor vendedor es {mejor_vendedor} con un total de ventas de ${total_ventas:.2f}."

        # Producto más vendido
        if "producto más vendido" in question:
            producto_mas_vendido = self.data['producto'].value_counts().index[0]
            cantidad = self.data['producto'].value_counts().iloc[0]
            return f"El producto más vendido es '{producto_mas_vendido}' con {cantidad} ventas."

        # Si no se encuentra una respuesta en el CSV
        return None

    def get_response(self, question: str, conversation: list):
        csv_answer = self.search_csv(question)
        if csv_answer:
            response_text = self.format_response(csv_answer)
        else:
            try:
                response = self.model.generate_content(question)
                if response.text:
                    response_text = self.format_response(response.text)
                else:
                    response_text = "<p>Lo siento, no pude generar una respuesta en este momento.</p>"
            except Exception as e:
                response_text = f"<p>Error al generar respuesta: {str(e)}</p>"
        
        conversation.append((question, response_text))
        return response_text, conversation
    def format_response(self, text):
    # Dividir el texto en párrafos
        paragraphs = text.split('\n')
        formatted_text = ""
        for para in paragraphs:
            if para.strip():
                if para.startswith("*"):
                    # Convertir asteriscos en viñetas
                    formatted_text += f"<li>{para.strip('* ')}</li>"
                elif para.startswith("**"):
                    # Convertir doble asterisco en subtítulos
                    formatted_text += f"<h3>{para.strip('* ')}</h3>"
                else:
                    formatted_text += f"<p>{para}</p>"
        
        if formatted_text.startswith("<li>"):
            formatted_text = f"<ul>{formatted_text}</ul>"
        
        return formatted_text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatgo')
def chatgo():
    return render_template('chatgo.html')

@app.route('/chat', methods=['POST'])
def chat_api():
    user_input = request.json.get('message')
    gc = GeminiChatbot()
    conversation = []  # Inicia la conversación como una lista vacía o recupérala de algún lugar
    response_text, conversation = gc.get_response(user_input, conversation)
    return jsonify({'response': response_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)