from input_data_generation.input_data_generator import InputDataGenerator

if __name__ == "__main__":
    seed = 0
    input_data_generator = InputDataGenerator(seed=seed)
    input_data = input_data_generator.generate_input_data()
    print(input_data)