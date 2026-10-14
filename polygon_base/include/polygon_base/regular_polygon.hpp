#ifndef POLYGON_BASE_REGULAR_POLYGON_HPP
#define POLYGON_BASE_REGULAR_POLYGON_HPP

#include <class_loader/interface_traits.hpp>

namespace polygon_base
{
  class RegularPolygon
  {
    public:
      virtual double area() = 0;
      virtual ~RegularPolygon() = default;

    protected:
      RegularPolygon() = default;
  };
}  // namespace polygon_base

// Interface traits specialized for our interface `polygon_base::RegularPolygon`
// to define constructor parameters.
template<>
struct class_loader::InterfaceTraits<polygon_base::RegularPolygon>
{
  // The constructor of the plugins will take a `double`.
  // You can use constructor with more arguments by listing them inside the
  // angle brackets.
  // Eg.: class_loader::ConstructorParameters<std::string, std::vector<int>>
  using constructor_parameters = class_loader::ConstructorParameters<double>;
};

#endif  // POLYGON_BASE_REGULAR_POLYGON_HPP