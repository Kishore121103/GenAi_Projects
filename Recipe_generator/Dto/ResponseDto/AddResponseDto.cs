using Recipe_generator.Models.Entities;
using System.ComponentModel.DataAnnotations.Schema;
using System.ComponentModel.DataAnnotations;

namespace Recipe_generator.Dto.ResponseDto
{
    public class AddResponseDto
    {
        public int MessageId { get; set; }
        public Guid SessionId { get; set; }
        public string Role { get; set; }
        public string Content { get; set; }
        public DateTime CreatedAt { get; set; }
    }
}
