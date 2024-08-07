import gradio as gr
import os
import pandas as pd
import google.generativeai as genai
from datetime import datetime


class GeminiChatbot:
    def __init__(self):
        self.init_gemini_chatbot()
        self.load_csv_data()

    def init_gemini_chatbot(self):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')

    def load_csv_data(self):
        # Cargar los datos del CSV
        self.data = pd.read_csv('ventas.csv')
        # Convertir la columna 'fecha' a datetime
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
        # Buscar la respuesta en el CSV
        csv_answer = self.search_csv(question)
        if csv_answer:
            response_text = csv_answer
        else:
            # Si no se encuentra en el CSV, usar el modelo generativo
            response = self.model.generate_content(question)
            response_text = response.text
        
        conversation.append((question, response_text))
        return "", conversation
    
    def launch_gradio(self):
        with gr.Blocks() as demo:
            chatbot = gr.Chatbot()
            question = gr.Textbox(label="Pregúntame")
            clear = gr.ClearButton([question, chatbot])

            question.submit(self.get_response, [question, chatbot], [question, chatbot])

        demo.launch(debug=True, server_name="0.0.0.0", server_port=5000)

if __name__ == "__main__":
    gc = GeminiChatbot()
    gc.launch_gradio()
