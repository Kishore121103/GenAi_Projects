using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Recipe_generator.data;
using Recipe_generator.Dto.RequestDto;
using Recipe_generator.Dto.ResponseDto;
using Recipe_generator.Models.Entities;
// Ensure correct namespace for ApplicationDbContext

namespace Recipe_generator.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class Message : ControllerBase
    {
        private readonly ApplicationDbContext _dbContext;

        // Constructor that takes ApplicationDbContext as a parameter
        public Message(ApplicationDbContext dbContext)
        {
            _dbContext = dbContext; // Assign to private field _dbContext
        }

        [HttpGet]
        public IActionResult GetAllResponse()
        {
            var allResponse = _dbContext.Messages.ToList(); // Assuming 'Messages' is the DbSet in ApplicationDbContext
            return Ok(allResponse);
        }

        [HttpGet("get-responses/{sessionId}")]
        public async Task<IActionResult> GetResponsesBySessionId(Guid sessionId)
        {
            // Validate the session ID
            if (sessionId == Guid.Empty)
            {
                return BadRequest("Invalid session ID.");
            }

            // Check if the session exists
            var sessionExists = await _dbContext.Sessions.AnyAsync(s => s.SessionId == sessionId);
            if (!sessionExists)
            {
                return NotFound("Session not found.");
            }

            // Retrieve all messages associated with the session ID
            var messages = await _dbContext.Messages
                .Where(m => m.SessionId == sessionId)
                .OrderBy(m => m.CreatedAt) // Optional: Sort messages by creation time
                .Select(m => new GetMessageDto
                {
                    MessageId = m.MessageId,
                    Role = m.Role,
                    Content = m.Content,
                    CreatedAt = m.CreatedAt
                })
                .ToListAsync();

            return Ok(messages);
        }


        [HttpPost("add-response")]
        public async Task<IActionResult> AddResponse([FromBody] AddResponseRequestDto dto)
        {
            if (dto == null || string.IsNullOrWhiteSpace(dto.Role) || string.IsNullOrWhiteSpace(dto.Content))
            {
                return BadRequest("Invalid request payload.");
            }

            if (string.IsNullOrWhiteSpace(dto.SessionId.ToString()))
            {
                return BadRequest("Session ID is required.");
            }

            var session = await _dbContext.Sessions.FindAsync(dto.SessionId);
            if (session == null)
            {
                return NotFound("Session not found. Please create a new session.");
            }

            session.LastUpdatedAt = DateTime.UtcNow;
            _dbContext.Sessions.Update(session);

            var message = new message
            {
                SessionId = dto.SessionId,
                Role = dto.Role,
                Content = dto.Content,
                CreatedAt = DateTime.UtcNow
            };

            await _dbContext.Messages.AddAsync(message);
            await _dbContext.SaveChangesAsync();

            var responseDto = new AddResponseDto
            {
                MessageId = message.MessageId,
                SessionId = message.SessionId,
                Role = message.Role,
                Content = message.Content,
                CreatedAt = message.CreatedAt
            };

            return CreatedAtAction(nameof(AddResponse), new { id = message.MessageId }, responseDto);
        }


        [HttpGet("get-sessions")]

        public async Task<IActionResult> GetSessions()
        {
            var sessions = await _dbContext.Sessions
                .OrderByDescending(s => s.LastUpdatedAt)
                .ToListAsync();
            return Ok(sessions);
        }

        [HttpPost("create-session")]
        public async Task<IActionResult> CreateSession()
        {
            var session = new session
            {
                SessionId = Guid.NewGuid(),
                CreatedAt = DateTime.UtcNow,
                LastUpdatedAt = DateTime.UtcNow
            };

            await _dbContext.Sessions.AddAsync(session);
            await _dbContext.SaveChangesAsync();

            return CreatedAtAction(nameof(CreateSession), new { id = session.SessionId }, new
            {
                sessionId = session.SessionId,
                createdAt = session.CreatedAt
            });
        }

        [HttpPost("add-items")]
        public async Task<IActionResult> AddItems([FromBody] AddItemsRequestDto request)
        {

            if (request.SessionId == Guid.Empty)
            {
                return BadRequest("Session ID is required.");
            }

            // Validate session ID
            var session = await _dbContext.Sessions.FindAsync(request.SessionId);
            if (session == null)
            {
                return NotFound("Session not found. Please provide a valid session.");
            }

            var groceryItems = request.Items.Select(item => new GroceryItem
            {
                SessionId = request.SessionId,
                ItemName = item.ItemName,
                Quantity = item.Quantity,
                PurchaseDate = item.PurchaseDate ?? DateTime.UtcNow, // Default to current date if not provided
                CreatedAt = DateTime.UtcNow
            }).ToList();

            // Add grocery items to the database
            await _dbContext.GroceryItems.AddRangeAsync(groceryItems);

            // Update session's last updated timestamp
            session.LastUpdatedAt = DateTime.UtcNow;
            _dbContext.Sessions.Update(session);

            await _dbContext.SaveChangesAsync();

            return Ok(new
            {
                Message = "Items added successfully.",
                Items = groceryItems.Select(g => new
                {
                    g.ItemName,
                    g.Quantity,
                    PurchaseDate = g.PurchaseDate.ToString("yyyy-MM-dd")
                })
            });
        }

        [HttpGet("get-items")]
        public async Task<IActionResult> GetAllItems()
        {
            var groceryItems = await _dbContext.GroceryItems
                .OrderBy(g => g.CreatedAt)  // Optional: Sort items by creation time
                .Select(g => new
                {   g.GroceryItemId,
                    g.ItemName,
                    g.Quantity,
                    PurchaseDate = g.PurchaseDate.ToString("yyyy-MM-dd"),
                    g.CreatedAt
                })
                .ToListAsync();

            return Ok(groceryItems);
        }

        [HttpPut("update-item/{itemId}")]
        public async Task<IActionResult> UpdateItem(Guid itemId, [FromBody] UpdateGroceryItemRequestDto request)
        {
            // Validate request payload
            if (request == null)
            {
                return BadRequest("Invalid request payload.");
            }

            //// Ensure all required properties are provided
            //if (string.IsNullOrWhiteSpace(request.ItemName) || request.Quantity != "")
            //{
            //    return BadRequest("Item name and quantity are required.");
            //}

            // Find the grocery item by its ID
            var groceryItem = await _dbContext.GroceryItems.FindAsync(itemId);
            if (groceryItem == null)
            {
                return NotFound("Grocery item not found.");
            }

            // Update the properties of the grocery item
            groceryItem.ItemName = request.ItemName;
            groceryItem.Quantity = request.Quantity;
            groceryItem.PurchaseDate = request.PurchaseDate ?? groceryItem.PurchaseDate; // Keep existing if not provided
            groceryItem.CreatedAt = DateTime.UtcNow; // Optionally update the creation date or just leave it unchanged

            // Save changes to the database
            _dbContext.GroceryItems.Update(groceryItem);
            await _dbContext.SaveChangesAsync();

            // Return the updated item as part of the response
            return Ok(new
            {
                groceryItem.ItemName,
                groceryItem.Quantity,
                PurchaseDate = groceryItem.PurchaseDate.ToString("yyyy-MM-dd"),
                groceryItem.CreatedAt
            });
        }

    }
}
