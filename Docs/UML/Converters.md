# UML-диаграммы конвертации объектов

## Диаграмма классов

```mermaid
classDiagram
    direction TB

    class abstract_converter {
        <<abstract>>
        +convert(field_name: str, value) dict
    }

    class basic_converter {
        +convert(field_name: str, value) dict
    }

    class datetime_converter {
        +convert(field_name: str, value) dict
    }

    class reference_converter {
        -Callable __convert_reference
        +convert(field_name: str, value) dict
    }

    class convert_factory {
        -basic_converter __basic_converter
        -datetime_converter __datetime_converter
        -reference_converter __reference_converter
        -list __path
        +create(value) abstract_converter
        +convert(source) dict
        -__convert_object(source) dict
        -__convert_field(field_name: str, value) dict
        -__get_field_names(source) list
    }

    class operation_error

    abstract_converter <|-- basic_converter
    abstract_converter <|-- datetime_converter
    abstract_converter <|-- reference_converter

    convert_factory *-- basic_converter
    convert_factory *-- datetime_converter
    convert_factory *-- reference_converter
    reference_converter ..> convert_factory : рекурсивный вызов
    convert_factory ..> operation_error : циклическая ссылка
```

## Последовательность конвертации

```mermaid
sequenceDiagram
    autonumber
    actor Client as Клиент
    participant Factory as convert_factory
    participant Converter as converter
    participant Reference as reference_converter

    Client->>Factory: convert(source)
    Factory->>Factory: __convert_field("value", source)
    Factory->>Reference: convert("value", source)
    Reference->>Factory: __convert_object(source)
    Factory->>Factory: получить публичные свойства

    loop Для каждого свойства
        Factory->>Factory: __convert_field(field_name, value)

        alt Простое значение
            Factory->>Factory: create(value)
            Factory->>Converter: convert(field_name, value)
            Converter-->>Factory: {field_name: value}
        else Дата и время
            Factory->>Factory: create(value)
            Factory->>Converter: convert(field_name, value)
            Converter-->>Factory: {field_name: ISO 8601}
        else Коллекция
            Factory->>Factory: __convert_field для каждого элемента
        else Ссылка на объект
            Factory->>Factory: create(value)
            Factory->>Reference: convert(field_name, value)
            Reference->>Factory: рекурсивно преобразовать объект
            Factory-->>Reference: вложенный словарь
            Reference-->>Factory: {field_name: dictionary}
        end
    end

    Factory-->>Reference: словарь полей объекта
    Reference-->>Factory: {value: словарь}
    Factory-->>Client: словарь исходной структуры
```
