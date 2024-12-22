namespace Recipe_generator.Dto.RequestDto
{
    public class UpdateGroceryItemRequestDto
    {
        public string ItemName { get; set; }
        public string Quantity { get; set; }
        public DateTime? PurchaseDate { get; set; }
    }
}
