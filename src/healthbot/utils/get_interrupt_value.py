def get_interrupt_value(interrupt_data, key, default="Not available"):
    """
    Safely extract values from interrupt data.

    Args:
        interrupt_data: The interrupt data from LangGraph
        key: The key to extract from the interrupt value
        default: Default value if key is not found

    Returns:
        The value for the given key, or default if not found
    """
    try:
        # Check if interrupt_data is a list and has items
        if isinstance(interrupt_data, list) and len(interrupt_data) > 0:
            interrupt_obj = interrupt_data[0]  # Get the first Interrupt object

            # Check if the object has a 'value' attribute
            if hasattr(interrupt_obj, 'value'):
                data = interrupt_obj.value
                # Return the value for the key, or default if key doesn't exist
                return data.get(key, default)
            else:
                return default
        else:
            return default
    except Exception as e:
        print(f"Error extracting interrupt value: {e}")
        return default
