namespace Recipe_generator.Dto.RequestDto
{
    public class AddItemsRequestDto
    {

        public Guid SessionId { get; set; }
        public List<GroceryItemDto> Items { get; set; }

    }
}

public class GroceryItemDto
{
    public string ItemName { get; set; }
    public string Quantity { get; set; }
    public DateTime? PurchaseDate { get; set; } // Optional
}